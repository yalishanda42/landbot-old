#!python3

"""LandBot - Discord chatbot serving the landcore community.

(c) 2020 Yalishanda.
"""

import discord
import logging


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


def _setup_logger():
    """Set up the logger."""
    logger = logging.getLogger("discord")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(
        filename="discord.log",
        encoding="utf-8",
        mode="w"
    )

    logformat = "%(asctime)s:%(levelname)s:%(name)s: %(message)s"
    handler.setFormatter(logging.Formatter(logformat))
    logger.addHandler(handler)


def _retrieve_token(filename="token"):
    """Get the access token that is located in the given file."""
    with open(filename, "r") as tokenfile:
        return tokenfile.read()[:-1]


if __name__ == "__main__":
    _setup_logger()

    client = LandBot()

    token = _retrieve_token()
    client.run(token)
