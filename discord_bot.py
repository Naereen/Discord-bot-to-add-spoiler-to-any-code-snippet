#!/usr/bin/env python3
#-*- coding: utf8 -*-
"""
This bot aims at automatically adding /spoiler to any code snippet pasted in a Discord text channel in your Discord server.

- Work in progress.
- See https://github.com/Naereen/Discord-bot-to-add-spoiler-to-any-code-snippet.git
- Author: Lilian Besson (Naereen)
- Date: 04/11/2020
- License: [MIT License](https://lbesson.mit-license.org/)
"""

import os
import random

# to speed up, define here the regexp and compile them
import re
start_codesnippet = re.compile("```[a-zA-Z]*\n")

from roles_lib import extract_role, sanitize_name, check_name, check_role


# API for getting jokes
import requests
URL = 'https://official-joke-api.appspot.com/random_joke'

def check_valid_status_code(request):
    """ If valid return code, return JSON from request."""
    if request.status_code == 200:
        return request.json()
    return False

def get_joke():
    """ Return JSON data from a random joke."""
    request = requests.get(URL)
    data = check_valid_status_code(request)
    return data


PATH_QUOTES = "quotes.txt"
quotes = [
    "\"En revoir, et merci bien pour le poisson !\" -- H2G2"
]
if os.path.exists(PATH_QUOTES):
    with open(PATH_QUOTES, 'r') as f:
        quotes = f.readlines()

def get_random_quote():
    """ Return random line of the file quotes.txt"""
    quote = random.choice(quotes)
    return quote





# See https://blog.alanconstantino.com/articles/creating-a-discord-bot-with-python.html
# https://discordpy.readthedocs.io/en/latest/api.html#discord-models
import discord
from discord.ext import commands

bot = commands.Bot(
    status = discord.Status.online,
    activity = discord.Game(name="Type !help for help"),
    command_prefix = "!",
    description = """
This bot aims at automatically adding /spoiler to any code snippet pasted in a Discord text channel in your Discord server.
When I see a message containing code between \`\`\`...\`\`\`, I remove the formatting and show the code as spoiler ||spoiler||.

Work in progress. See https://github.com/Naereen/Discord-bot-to-add-spoiler-to-any-code-snippet.git
"""
)

# Print info when connected
@bot.event
async def on_ready():
    """ Function called when bot is ready (has logged in)."""
    print(f"This bot has logged in as '{bot.user}'")

    # See https://realpython.com/how-to-make-a-discord-bot-python/
    for guild in bot.guilds:
        print(
            f"\n\n'{bot.user}' is connected to the following guild:\n"
            f"'{guild.name}' (id: '{guild.id}')\n"
        )
        print(f"Guild Members:")
        for member in guild.members:
            print(f"- '{member.display_name}' (id: '{member.id}')")


# Welcome a new member
@bot.event
async def on_member_join(member):
    """ Function called when bot sees a new member."""
    await member.create_dm()
    # TODO check if member name is Prénom NOM - IE-?? ou Prénom Nom - MA?-?
    # TODO if name is correct, add to the good role
    if not check_name(member.display_name):
        member.add_roles([
            "TODO"
        ], reason=f"Adding user '{member.display_name}' to role 'TODO'.")
        await member.dm_channel.send(
f""":wave: Bonjour @{member.display_name}, et bienvenue sur ce serveur Discord !
:point_right: STP, change ton pseudo sous la forme *Prénom NOM - groupe*, par exemple *Marie DUPONT - IE-1A* ou *Luc SKYWALKER - MA4-8*, pour que je puisse t'ajouter à ton groupe de TP.
N'hésite pas à explorer l'organisation du serveur, à poser des questions dans les jours qui viennent (dans le salon correspondant à ton groupe, ou dans #questions-organisation-discord).
Bon courage pour ce confinement."""
        )
    else:
        print(f"Removing role 'TODO' of user '{member.display_name}'")
        role = extract_role(member.display_name)
        member.remove_roles([
            "TODO"
        ], reason=f"Removing user '{member.display_name}' from role 'TODO'.")
        print(f"Adding role '{role}' of user '{member.display_name}'")
        member.add_roles([role], reason=f"Adding user '{member.display_name}' to role '{role}' because of its pseudo.")
        await member.dm_channel.send(
f""":wave: Bonjour @{member.display_name}, et bienvenue sur ce serveur Discord !
:ok_hand: J'ai lu ton pseudo, et j'ai pu détecter ton groupe {role}.
N'hésite pas à explorer l'organisation du serveur, à poser des questions dans les jours qui viennent (dans le salon correspondant à ton groupe, ou dans #questions-organisation-discord).
Bon courage pour ce confinement."""
        )

# TODO this does not work (yet)
# Check if the new pseudo of a user is now in a good form, and add him/her to the good group
@bot.event
async def on_member_update(before, after):
    print(f"{before.display_name} ({before.id}) changed his/her name to {after.display_name}")
    before_role = extract_role(before.display_name)
    after_role = extract_role(before.display_name)
    if (not check_name(before.display_name) or before_role == 'TODO') and (check_name(after.display_name) and after_role != 'TODO'):
        # TODO add him/her to good group
        print(f"Removing role 'TODO' of user '{before.display_name}'")
        role = extract_role(before.display_name)
        before.remove_roles([
            "TODO"
        ], reason=f"Removing user '{before.display_name}' from role 'TODO'.")

        print(f"Adding role '{role}' of user '{before.display_name}'")
        before.add_roles([role], reason=f"Adding user '{before.display_name}' to role '{role}' because of its pseudo.")

        await before.dm_channel.send(
f""":ok_hand: J'ai lu ton pseudo, et j'ai pu détecter ton groupe {role}."""
        )



# basic command
@bot.command(name='hello', help="to check if the bot works, reply with 'Hello world!'")
async def hello(ctx):
    await ctx.send('Hello world!')

@bot.command(name='bonjour', help="vérifie que le bot marche, réponds avec 'Bonjour, le monde !'")
async def bonjour(ctx):
    await ctx.send('Bonjour, le monde !')


# brooklyn 99 quotes
brooklyn_99_quotes = [
    "I'm the human form of the 💯 emoji.",
    "Bingpot!",
    (
        "Cool. Cool cool cool cool cool cool cool, "
        "no doubt no doubt no doubt no doubt."
    ),
]
@bot.command(name='99', help="print a random quote from Brooklyn 99 (example)")
async def nine_nine(ctx):
    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)


# roi loth

try:
    from Generer_des_fausses_citations_latines_du_Roi_Loth import citation_aleatoire
except ImportError:
    roi_loth_quotes = [
        """> *Ave Cesar, rosae rosam, et spiritus rex !* Ah non, parce que là, j'en ai marre !
        > -- François Rollin, Kaamelott, Livre III, L'Assemblée des rois 2e partie, écrit par Alexandre Astier.""",

        """> *Tempora mori, tempora mundis recorda*. Voilà. Eh bien ça, par exemple, ça veut absolument rien dire, mais l'effet reste le même, et pourtant j'ai jamais foutu les pieds dans une salle de classe attention !
        > -- François Rollin, Kaamelott, Livre III, L'Assemblée des rois 2e partie, écrit par Alexandre Astier.""",

        """> *Victoriae mundis et mundis lacrima.* Bon, ça ne veut absolument rien dire, mais je trouve que c'est assez dans le ton.
        > -- François Rollin, Kaamelott, Livre IV, Le désordre et la nuit, écrit par Alexandre Astier.""",

        """> *Misa brevis et spiritus maxima*, ça veut rien dire, mais je suis très en colère contre moi-même.
        > -- François Rollin, Kaamelott, Livre V, Misère noire, écrit par Alexandre Astier.""",

        """> *Deus minimi placet* : seul les dieux décident.
        > -- François Rollin, Kaamelott, Livre VI, Arturus Rex, écrit par Alexandre Astier.""",

        """> *"Mundi placet et spiritus minima"*, ça n'a aucun sens mais on pourrait très bien imaginer une traduction du type : *"Le roseau plie, mais ne cède... qu'en cas de pépin"* ce qui ne veut rien dire non plus.
        > -- François Rollin, Kaamelott, Livre VI, Lacrimosa, écrit par Alexandre Astier.""",

    ]
    def citation_aleatoire():
        return random.choice(roi_loth_quotes)

@bot.command(name='roiloth', help="prints a random fake quote from Roi Loth (Kaamelott) TODO")
async def roiloith(ctx, number_of_citations: int):
    if number_of_citations <= 0:
        number_of_citations = 1
    for _ in range(number_of_citations):
        response = citation_aleatoire()
        await ctx.send(response)


# keep the Joke bot
@bot.command(name='joke', help="prints a random joke")
async def joke(ctx):
    # bot.trigger_typing()
    joke = get_joke()
    if joke == False:
        await ctx.send(f"Couldn't get joke from API ({URL}). Try again later.")
    else:
        await ctx.send(joke['setup'] + '\n' + joke['punchline'])

# add a quote bot
@bot.command(name='quote', help="prints a random quote")
async def quote(ctx):
    await ctx.message.delete(delay=1)
    quote = get_random_quote()
    if quote:
        await ctx.send(quote)

# https://realpython.com/how-to-make-a-discord-bot-python/
@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')


@bot.event
async def on_message(message):
    # don't react to message posted by the post!
    if message.author == bot.user:
        return
    print(message.content)

    # happy birthday feature
    if 'happy birthday' in message.content.lower():
        await message.channel.send(f"Happy Birthday @{message.author.display_name}! 🎈🎉")
    if 'joyeux anniversaire' in message.content.lower():
        await message.channel.send(f"Joyeux anniversaire @{message.author.display_name} ! 🎈🎉")

    # now implement the anti spoiler bot
    if '```' in message.content:
        # TODO delete the message!
        try:
            print("Trying to deleting message...")
            await message.delete()
            print("Successfully deleting message.")
        except discord.errors.Forbidden:
            print("Failed to delete message.")

        print("\nReading a new code snippet... I should ||anti spoiler|| it!")
        await message.channel.send(spoiler_code_snippet(message.content))

        # Another idea: delete the initial message, and post its content as a file, with spoiler enabled
        # spoiler = await file.to_file(spoiler=True)
        # await ctx.send(file=spoiler)

        # # now run the code TODO
        # await message.channel.send("Also running the code snippet using @RTFM bot...")
        # await message.channel.send(f"do run {used_language} {content}")
    else:
        await bot.process_commands(message) # allows decorated commands to work


def spoiler_code_snippet(content):
        print(f"Calling spoiler_code_snippet() on:\n{content}")
        # DONE use a regexp to work for all languages
        # TODO handle correctly code in different languages
        used_language = start_codesnippet.search(content)[0]
        used_language = used_language.replace('```', '', 1).replace('\n', '', 1)
        if used_language:
            print(f"This code snippet is using '{used_language}' language")

        # TODO only do this for the part of the content which is between ```...```
        content = content.replace(f'```{used_language}\n', f'```\n')
        pieces = content.split('```')
        new_pieces = []
        for i, piece in enumerate(pieces):
            new_piece = piece
            if i % 2 == 1:
                # protect special characters, only on odd-numbered pieces
                # as they are the ones between ```java ...```
                new_piece = new_piece.replace('|', r'\|')
                new_piece = new_piece.replace('`', r'\`')
                new_piece = new_piece.replace('*', r'\*')
                new_piece = new_piece.replace('_', r'\_')
                new_piece = new_piece.replace('~', r'\~')
                new_piece = new_piece.replace('>', r'\>')
                new_piece = new_piece.replace(r'\`||', '`||')
                new_piece = new_piece.replace(r'||\`', '||`')
            new_pieces.append(new_piece)

        content = '```'.join(new_pieces)
        content = content.replace(f'```\n', '\n||')
        content = content.replace('\n```', '||')

        if used_language:
            return f"Code (in {used_language}), click to unspoil :\n{content}"
        else:
            return f"Code, click to unspoil :\n{content}"


if __name__ == '__main__':
    with open("bot.token", 'r') as f:
        TOKEN = f.readline()
    bot.run(TOKEN)
