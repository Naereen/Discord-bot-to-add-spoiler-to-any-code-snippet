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

client = discord.Client(
    status = discord.Status.online,
    activity = discord.Game(name="Type /help for help"),
)

# Print info when connected
@client.event
async def on_ready():
    """ Function called when bot is ready (has logged in)."""
    print(f"This bot has logged in as '{client.user}'")

    # See https://realpython.com/how-to-make-a-discord-bot-python/
    for guild in client.guilds:
        print(
            f"\n\n'{client.user}' is connected to the following guild:\n"
            f"'{guild.name}' (id: '{guild.id}')\n"
        )
        print(f"Guild Members:")
        for member in guild.members:
            print(f"- '{member.display_name}' (id: '{member.id}')")


# Welcome a new member
@client.event
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
@client.event
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



# brooklyn 99 quotes
brooklyn_99_quotes = [
    "I'm the human form of the 💯 emoji.",
    "Bingpot!",
    (
        "Cool. Cool cool cool cool cool cool cool, "
        "no doubt no doubt no doubt no doubt."
    ),
]

@client.event
async def on_message(message):
    # don't react to message posted by the post!
    if message.author == client.user:
        return

    # basic command
    if message.content.startswith('/hello'):
        await message.channel.send('Hello world!')
    if message.content.startswith('/bonjour'):
        await message.channel.send('Bonjour, le monde !')

    # print help
    if message.content.startswith('/help') or message.content.startswith('/aide'):
        await message.author.create_dm()
        await message.author.dm_channel.send(
            """Help for the bot:

- /hello: to check if the bot works, reply with 'Hello world!'
- /help: displays this help.
- happy birthday: reply with a happy birthday message.
- /joke: prints a random joke in English (example)
- /quote: prints a random joke in English (example)
- 99!: print a random quote from Brooklyn 99 (example)
- When I see a message containing code between \`\`\`java...\`\`\`, I remove the formatting and show the code as spoiler ||spoiler||.
            """
        )

    # happy birthday feature
    if 'happy birthday' in message.content.lower():
        await message.channel.send(f"Happy Birthday @{message.author.display_name}! 🎈🎉")
    if 'joyeux anniversaire' in message.content.lower():
        await message.channel.send(f"Joyeux anniversaire @{message.author.display_name} ! 🎈🎉")

    # brooklyn 99 quotes
    if message.content == '99!':
        response = random.choice(brooklyn_99_quotes)
        await message.channel.send(response)

    # keep the Joke bot
    if message.content.startswith('/joke') or message.content.startswith('/blague'):
        # client.trigger_typing()
        joke = get_joke()

        if joke == False:
            await message.channel.send("Couldn't get joke from API. Try again later.")
        else:
            await message.channel.send(joke['setup'] + '\n' + joke['punchline'])

    # add a quote bot
    if message.content.startswith('/quote') or message.content.startswith('/citation'):
        # client.trigger_typing()
        quote = get_random_quote()
        if quote:
            await message.channel.send(quote)

    # now implement the anti spoiler bot
    if '```' in message.content:
        # TODO delete the message!
        try:
            await message.delete()
            print("Successfully deleting message.")
        except discord.errors.Forbidden:
            print("Failed to delete message.")
        print("Reading a code snippet... I should /spoiler it!")
        content = message.content
        # DONE use a regexp to work for all languages
        used_language = start_codesnippet.search(content)[0]
        used_language = used_language.replace('```', '', 1).replace('\n', '', 1)
        if used_language:
            print(f"This code snippet is using '{used_language}' language")

        content = content.replace('|', r'\|')
        content = content.replace(f'```{used_language}\n', '\n||')
        content = content.replace('\n```', '||')
        content = content.replace('`', r'\`')
        content = content.replace('*', r'\*')
        content = content.replace('_', r'\_')
        content = content.replace('~', r'\~')
        content = content.replace('>', r'\>')
        content = content.replace(r'\`||', '`||')
        content = content.replace(r'||\`', '||`')
        if used_language:
            await message.channel.send(f"Code ({used_language}), click to unspoil :\n{content}`")
        else:
            await message.channel.send(f"Code, click to unspoil :\n{content}")

        # # now run the code TODO
        # await message.channel.send("Also running the code snippet using @RTFM bot...")
        # await message.channel.send(f"do run {used_language} {content}")


if __name__ == '__main__':
    tests(verbose=False)

    with open("bot.token", 'r') as f:
        TOKEN = f.readline()
    client.run(TOKEN)
