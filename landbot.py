#!python3

"""LandBot - Discord chatbot serving the landcore community.

(c) 2020 Yalishanda.
"""

import discord

client = discord.Client()


@client.event
async def on_ready():
    """Ouput useful debugging information."""
    print(f"Bot logged in as {client.user}.")


@client.event
async def on_message(message):
    """Listen for messages starting with '!' and execute their commands."""
    if message.author == client.user:
        return

    if message.content.startswith("!test"):
        await message.channel.send("Test? Why not.\nI am the best bot.")


with open("token", "r") as tokenfile:
    token = tokenfile.read()[:-1]
    client.run(token)
