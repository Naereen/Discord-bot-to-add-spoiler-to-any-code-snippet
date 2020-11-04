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
import re
import random

# to speed up, define here the regexp and compile them
start_codesnippet = re.compile("```[a-zA-Z]*\n")


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


def extract_role(name):
    """ Extract the role from given username."""
    name = sanitize_name(name)
    if ' - prof' in name:
        return "prof"
    for l in [1,2,3,4,5,6,7,8,9]:
        for g in ["A", "B"]:
            role = f'IE-{l}{g}'
            if name.endswith(role):
                return role
    for l in [1,2,3,4]:
        for g in [2*l-1, 2*l]:
            role = f'MA{l}-{g}'
            if name.endswith(role):
                return role
    return "TODO"

# TODO sanitize pseudo of a user
def sanitize_name(name):
    """ Clean-up the given username."""
    name = name.strip()

    # clean up group
    name = name.replace('- IE', ' -IE')
    name = name.replace('- MA', ' -MA')
    for l in [1,2,3,4,5,6,7,8,9]:
        for g in "AB":
            name = name.replace(f'IE{l}-{g}', f'IE-{l}{g}')
            name = name.replace(f'IE{l}{g}', f'IE-{l}{g}')
    for l in [1,2,3,4]:
        for g in [2*l-1, 2*l]:
            name = name.replace(f'MA-{l}{g}', f'MA{l}-{g}')
            name = name.replace(f'MA{l}{g}', f'MA{l}-{g}')

    # clean up name
    try:
        parts = name.split(' ')
        firstname = parts[0].title()
        group = parts[-1]
        familynames = parts[1:-1]
        familyname = " ".join(f.upper() for f in familynames)
        name = f"{firstname} {familyname} {group}"
        name = name.replace('-IE', '- IE')
        name = name.replace('-MA', '- MA')
    except:
        pass
    while "  " in name:
        name = name.replace('  ', ' ')
    return name

letters = list("abcdefghijklmnopqrstuvwxyz") + list("ààâçéèêäôöîïùûüŷÿñ")
LETTERS = [l.upper() for l in letters]
numbers = list("123456789")
all_letters = set(letters + LETTERS + numbers + [" ", "-", "'"])

# TODO
def check_name(name):
    """ check if the pseudo of a user is valid."""
    name = sanitize_name(name)
    for letter in name:
        if letter not in all_letters:
            # print(f"Bad letter = {letter}")
            return False
    role = extract_role(name)
    # remove group
    name = name.replace(f' - {role}', '')
    try:
        parts = name.split(' ')
        firstname = parts[0].title()
        if firstname[0] not in letters:
            return False
        for letter in firstname[1:]:
            if letter not in LETTERS:
                return False
        familynames = parts[1:]
        for familyname in familynames:
            if familyname[0] not in letters:
                return False
            for letter in familyname[1:]:
                if letter not in LETTERS:
                    return False
        return True
    except:
        return False

# List of roles
roles = ["prof", "TODO"] + [
        f"IE-{l}{g}" for l in [1,2,3,4,5,6,7,8,9] for g in ["A", "B"]
    ] + [
        f"MA{l}-{g}" for l in [1,2,3,4] for g in [2*l-1, 2*l]
    ]
all_roles = set(roles)

def check_role(role):
    """ check if role is correct."""
    return role in all_roles

def tests(verbose=True):
    """ use good_names.txt and bad_names.txt to test previous functions."""
    # good names
    names = []
    with open("tests/good_names.txt") as f:
        for line in f.readlines():
            line = line.replace('\n', '')
            if line and not line.startswith("#"):
                names.append(line)
    for name in names:
        if verbose:
            print(f"'{name}' --> '{sanitize_name(name)}' of group '{extract_role(name)}'")
        # assert check_name(name)
        role = extract_role(name)
        assert check_role(role) and role != "TODO"

    # bad names
    names = []
    with open("tests/bad_names.txt") as f:
        for line in f.readlines():
            line = line.replace('\n', '')
            if line and not line.startswith("#"):
                names.append(line)
    for name in names:
        if verbose:
            print(f"'{name}' --> '{sanitize_name(name)}' of group '{extract_role(name)}'")
        # assert check_name(name)
        role = extract_role(name)
        assert (not check_name(name)) or (role == "TODO")


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
When I see a message containing code between \`\`\`java...\`\`\`, I remove the formatting and show the code as spoiler ||spoiler||.

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



# # basic command
# @bot.command(name='hello', help="to check if the bot works, reply with 'Hello world!'")
# async def hello(ctx):
#     await ctx.send('Hello world!')

# @bot.command(name='bonjour', help="vérifie que le bot marche, réponds avec 'Bonjour, le monde !'")
# async def bonjour(ctx):
#     await ctx.send('Bonjour, le monde !')


# # brooklyn 99 quotes
# brooklyn_99_quotes = [
#     "I'm the human form of the 💯 emoji.",
#     "Bingpot!",
#     (
#         "Cool. Cool cool cool cool cool cool cool, "
#         "no doubt no doubt no doubt no doubt."
#     ),
# ]
# @bot.command(name='99', help="print a random quote from Brooklyn 99 (example)")
# async def nine_nine(ctx):
#     response = random.choice(brooklyn_99_quotes)
#     await ctx.send(response)


# # roi loth
# roi_loth_quotes = [
#     """> *Ave Cesar, rosae rosam, et spiritus rex !* Ah non, parce que là, j'en ai marre !
#     > -- François Rollin, Kaamelott, Livre III, L'Assemblée des rois 2e partie, écrit par Alexandre Astier.""",

#     """> *Tempora mori, tempora mundis recorda*. Voilà. Eh bien ça, par exemple, ça veut absolument rien dire, mais l'effet reste le même, et pourtant j'ai jamais foutu les pieds dans une salle de classe attention !
#     > -- François Rollin, Kaamelott, Livre III, L'Assemblée des rois 2e partie, écrit par Alexandre Astier.""",

#     """> *Victoriae mundis et mundis lacrima.* Bon, ça ne veut absolument rien dire, mais je trouve que c'est assez dans le ton.
#     > -- François Rollin, Kaamelott, Livre IV, Le désordre et la nuit, écrit par Alexandre Astier.""",

#     """> *Misa brevis et spiritus maxima*, ça veut rien dire, mais je suis très en colère contre moi-même.
#     > -- François Rollin, Kaamelott, Livre V, Misère noire, écrit par Alexandre Astier.""",

#     """> *Deus minimi placet* : seul les dieux décident.
#     > -- François Rollin, Kaamelott, Livre VI, Arturus Rex, écrit par Alexandre Astier.""",

#     """> *"Mundi placet et spiritus minima"*, ça n'a aucun sens mais on pourrait très bien imaginer une traduction du type : *"Le roseau plie, mais ne cède... qu'en cas de pépin"* ce qui ne veut rien dire non plus.
#     > -- François Rollin, Kaamelott, Livre VI, Lacrimosa, écrit par Alexandre Astier.""",

# ]

# @bot.command(name='roiloth', help="prints a random fake quote from Roi Loth (Kaamelott) TODO")
# async def roiloith(ctx):
#     response = random.choice(roi_loth_quotes)
#     await ctx.send(response)


# # keep the Joke bot
# @bot.command(name='joke', help="prints a random joke")
# async def joke(ctx):
#     # bot.trigger_typing()
#     joke = get_joke()
#     if joke == False:
#         await ctx.send(f"Couldn't get joke from API ({URL}). Try again later.")
#     else:
#         await ctx.send(joke['setup'] + '\n' + joke['punchline'])

# # add a quote bot
# @bot.command(name='quote', help="prints a random quote")
# async def quote(ctx):
#     quote = get_random_quote()
#     if quote:
#         await ctx.send(quote)

# # https://realpython.com/how-to-make-a-discord-bot-python/
# @bot.command(name='roll_dice', help='Simulates rolling dice.')
# async def roll(ctx, number_of_dice: int, number_of_sides: int):
#     dice = [
#         str(random.choice(range(1, number_of_sides + 1)))
#         for _ in range(number_of_dice)
#     ]
#     await ctx.send(', '.join(dice))


# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.errors.CheckFailure):
#         await ctx.send('You do not have the correct role for this command.')


@bot.listen('on_message')
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
            await message.delete()
            print("Successfully deleting message.")
        except discord.errors.Forbidden:
            print("Failed to delete message.")

        print("\nReading a new code snippet... I should ||anti spoiler|| it!")
        content = message.content
        print(content)
        # DONE use a regexp to work for all languages
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
                # protect special characters
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
            await message.channel.send(f"Code (in {used_language}), click to unspoil :\n{content}")
        else:
            await message.channel.send(f"Code, click to unspoil :\n{content}")

        # # now run the code TODO
        # await message.channel.send("Also running the code snippet using @RTFM bot...")
        # await message.channel.send(f"do run {used_language} {content}")


if __name__ == '__main__':
    tests(verbose=False)

    with open("bot.token", 'r') as f:
        TOKEN = f.readline()
    bot.run(TOKEN)
