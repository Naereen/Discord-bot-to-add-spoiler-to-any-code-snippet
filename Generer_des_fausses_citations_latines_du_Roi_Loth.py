import os
import random

from string import ascii_lowercase
from collections import Counter, defaultdict
from functools import lru_cache


# Le module [lea](https://bitbucket.org/piedenis/lea) sera très pratique pour manipuler les probabilités pour les chaînes de Markov.

from lea import Lea

# https://bitbucket.org/piedenis/lea/wiki/Lea3_Tutorial_2#markdown-header-markov-chains
from lea import markov


# don't recompute twice this, it takes some time!
@lru_cache(maxsize=None)
def old_markov(corpus, start, length):
    # Counting occurrences
    next_one = defaultdict(Counter)
    for sentence in corpus:
        words = sentence.split()
        nb_words = len(words)
        for i in range(nb_words - 1):
            next_one[words[i]][words[i + 1]] += 1

    # Initializing states
    states = {}
    for word in next_one:
        states[word] = Lea.fromValFreqsDict(next_one[word])

    # Outputting visited states
    word = start
    words = [word]
    for _ in range(length - 1):
        word = states[word].random()
        words.append(word)
    return(words)


# don't recompute twice this, it takes some time!
# @lru_cache(maxsize=None)
def make_markov(start, length, corpus=None, predefined_markov_chain=None):
    if predefined_markov_chain is None:
        # creating long sequences of observed states
        observed_states = []

        # Counting occurrences
        for sentence in corpus:
            words = sentence.split()
            observed_states += words

        # Initializing states
        markov_chain = markov.chain_from_seq(observed_states)
    else:
        markov_chain = predefined_markov_chain

    states = markov_chain.get_states()
    possible_starting_states = [ s for s in states if str(s).split(' : ')[0] == start ]
    if not possible_starting_states:
        starting_state = random.choice(states)
    else:
        starting_state = possible_starting_states[0]
    return starting_state.random_seq(length)


# ## Fausses locutions latines
#
# On va extraire le corpus, la liste des premiers mots, et la probabilité qu'un mot en début de citation commence par une majuscule.


WORD_LIST = "tests/latin.txt"
corpus = open(WORD_LIST).readlines()


if __name__ == "__main__":
    print("Exemple d'une citation :", corpus[0])
    print("Il y a", len(corpus), "citations.")


starts = [c.split()[0] for c in corpus]


if __name__ == "__main__":
    start = random.choice(starts)
    print("Exemple d'un mot de début de citation :", start)
    print("Il y a", len(starts), "mots de débuts de citations.")


    proba_title = len([1 for s in starts if s.istitle()]) / len(starts)
    print("Il y a {:.3%} chance de commencer une citation par une majuscule.".format(proba_title))


# Mais en fait, le Roi Loth commence toujours ses citations latines par une majuscule :

proba_title = 1


# On va générer des locutions de 3 à 6 mots :

length_min = 3
length_max = 6


# creating long sequences of observed states
observed_states = []

# Counting occurrences
for sentence in corpus:
    words = sentence.split()
    observed_states += words

# Initializing states
markov_chain = markov.chain_from_seq(observed_states)


# On a bientôt ce qu'il faut pour générer une locution latine aléatoire.
# Il arrive que la chaîne de Markov se bloque, donc on va juste essayer plusieurs fois avec des débuts différents.

def markov_try_while_failing(corpus, starts, length_min, length_max, proba_title, nb_max_trial=100, predefined_markov_chain=markov_chain):
    # Try 100 times to generate a sentence
    start = random.choice(starts)
    length = random.randint(length_min, length_max)
    for trial in range(nb_max_trial):
        try:
            words = list(make_markov(start, length, corpus=tuple(corpus), predefined_markov_chain=predefined_markov_chain))
            if random.random() <= proba_title:
                words[0] = words[0].title()
            return words  # comment to debug
            print(' '.join(words))
            break
        except KeyError:
            start = random.choice(starts)
            length = random.randint(length_min, length_max)
            continue
    raise ValueError("Echec")


# On peut essayer :

if __name__ == "__main__":
    for _ in range(10):
        words = markov_try_while_failing(corpus, starts, length_min, length_max, proba_title)
        print(' '.join(words))


# Ça a déjà l'air pas mal latin !

# ## Fausses citations du Roi Loth
#
# Pour générer une citation du Roi Loth, il ne suffit pas d'avoir des locutions latines.
# Il faut le contexte, l'explication, une fausse citation d'un épisode de Kaamelott etc...
#
# ### Premier exemple
# Ecouter celle là : [Misa brevis, et spiritus maxima](https://kaamelott-soundboard.2ec0b4.fr/#son/tres_en_colere).
# <audio src="data/tres_en_colere.mp3" controls="controls">Your browser does not support the audio element.</audio>
#
# ### Exemples
#
# > *Ave Cesar, rosae rosam, et spiritus rex !* Ah non, parce que là, j'en ai marre !
# > -- François Rollin, Kaamelott, Livre III, L'Assemblée des rois 2e partie, écrit par Alexandre Astier.
#
# > *Tempora mori, tempora mundis recorda*. Voilà. Eh bien ça, par exemple, ça veut absolument rien dire, mais l'effet reste le même, et pourtant j'ai jamais foutu les pieds dans une salle de classe attention !
# > -- François Rollin, Kaamelott, Livre III, L'Assemblée des rois 2e partie, écrit par Alexandre Astier.
#
# > *Victoriae mundis et mundis lacrima.* Bon, ça ne veut absolument rien dire, mais je trouve que c'est assez dans le ton.
# > -- François Rollin, Kaamelott, Livre IV, Le désordre et la nuit, écrit par Alexandre Astier.
#
# > *Misa brevis et spiritus maxima*, ça veut rien dire, mais je suis très en colère contre moi-même.
# > -- François Rollin, Kaamelott, Livre V, Misère noire, écrit par Alexandre Astier.
#
# > *Deus minimi placet* : seul les dieux décident.
# > -- François Rollin, Kaamelott, Livre VI, Arturus Rex, écrit par Alexandre Astier.
#
# > *"Mundi placet et spiritus minima"*, ça n'a aucun sens mais on pourrait très bien imaginer une traduction du type : *"Le roseau plie, mais ne cède... qu'en cas de pépin"* ce qui ne veut rien dire non plus.
# > -- François Rollin, Kaamelott, Livre VI, Lacrimosa, écrit par Alexandre Astier.

# ### Générer aléatoirement les métadonnées de l'épisode
# C'est facile.

episodes = [
    "Livre III, L'Assemblée des rois 2e partie, écrit par Alexandre Astier.",
    "Livre III, L'Assemblée des rois 2e partie, écrit par Alexandre Astier.",  # présent deux fois
    "Livre IV, Le désordre et la nuit, écrit par Alexandre Astier.",
    "Livre V, Misère noire, écrit par Alexandre Astier.",
    "Livre VI, Arturus Rex, écrit par Alexandre Astier.",
    "Livre VI, Lacrimosa, écrit par Alexandre Astier."
]


def metadonnee_aleatoire(episodes=episodes):
    episode = random.choice(episodes)
    return "D'après François Rollin, inspiré par Kaamelott, " + episode


# ### Générer aléatoirement les explications foireuses du Roi Loth
# C'est moins facile... Mais sans chercher à être parfait, on va juste prendre une explication parmi celles qui existent :

explications = [
    ". Ah non, parce que là, j'en ai marre !",
    ". Voilà. Eh bien ça, par exemple, ça veut absolument rien dire, mais l'effet reste le même, et pourtant j'ai jamais foutu les pieds dans une salle de classe attention !",
    ". Bon, ça ne veut absolument rien dire, mais je trouve que c'est assez dans le ton.",
    ", ça veut rien dire, mais je suis très en colère contre moi-même.",
    " : seul les dieux décident.",
    """, ça n'a aucun sens mais on pourrait très bien imaginer une traduction du type : "Le roseau plie, mais ne cède... qu'en cas de pépin", ce qui ne veut rien dire non plus.""",
]


# Et quelques variations :

explications += [
    ". Ah non, parce qu'au bout d'un moment, zut !",
    ". Voilà, ça ne veut rien dire, mais c'est assez dans le ton !",
    ". Bon, ça n'a aucun sens, mais j'aime bien ce petit ton décalé.",
    ". Le latin, ça impressionne ! Surtout les grouillots.",
    ", ça n'a aucun sens, mais je suis très en colère contre moi-même.",
    ", ça n'a aucun sens, mais je fais ça par amour.",
    " : la victoire par la sagesse.",
    " : les livres contiennent la sagesse des anciens.",
    " : à Rome seul compte le pouvoir.",
    " : seul les puissants agissent.",
    " : le mariage est une bénédiction.",
    " : ça veut rien dire, mais ça impressionne !",
    """, ça veut rien dire mais on pourrait très bien imaginer une traduction du type : "Le vent tourne pour ceux qui savent écouter", ce qui ne veut rien dire non plus.""",
    """, ça n'a aucun sens mais pourquoi pas une traduction du genre : "Les imbéciles dorment, les forts agissent mais dorment aussi", ce qui n'a aucun sens non plus.""",
]


def explication_aleatoire():
    return random.choice(explications)


# ### Combiner le tout !
# C'est très facile :

def citation_aleatoire(italic=False, quote=False):
    metadonnee = metadonnee_aleatoire()
    explication = explication_aleatoire()
    words = markov_try_while_failing(corpus, starts, length_min, length_max, proba_title)
    locution = ' '.join(words)
    citation = f"{'> ' if quote else ''}\"{'*' if italic else ''}{locution}{'*' if italic else ''}\"{explication} -- {metadonnee}"
    return citation


# ### Exemples

if __name__ == "__main__":
    for _ in range(10):
        print(">", citation_aleatoire(italic=True))

