#!python3

"""LandBot - Discord chatbot serving the landcore community.

(c) 2020 Yalishanda.
"""

import discord


class LandBot(discord.Client):
    """Bot implementation."""

    async def on_ready(self):
        """Ouput useful debugging information."""
        print(f"Bot logged in as {self.user}.")

    async def on_message(self, message):
        """Listen for messages starting with '!' and execute their commands."""
        if message.author == self.user:
            return

        if message.content.startswith("!test"):
            await message.channel.send("Test? Why not.\nI am the best bot.")


if __name__ == "__main__":
    client = LandBot()
    with open("token", "r") as tokenfile:
        token = tokenfile.read()[:-1]
        client.run(token)
