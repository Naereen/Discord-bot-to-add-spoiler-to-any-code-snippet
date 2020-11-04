#!/usr/bin/env python3
#-*- coding: utf8 -*-

# See https://blog.alanconstantino.com/articles/creating-a-discord-bot-with-python.html

import discord

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$joke'):
        joke = get_joke()

        if joke == False:
            await message.channel.send("Couldn't get joke from API. Try again later.")
        else:
            await message.channel.send(joke['setup'] + '\n' + joke['punchline'])


import requests

URL = 'https://official-joke-api.appspot.com/random_joke'


def check_valid_status_code(request):
    if request.status_code == 200:
        return request.json()
    return False


def get_joke():
    request = requests.get(URL)
    data = check_valid_status_code(request)
    return data


if __name__ == '__main__':
    with open("bot.token", 'r') as f:
        TOKEN = f.readline()
    client.run(TOKEN)
