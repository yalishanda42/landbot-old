#!python3

"""LandBot - Discord chatbot serving the landcore community.

(c) 2020 Yalishanda.
"""

import discord
import logging
import re
import transliterate

from rimichka import RimichkaAPI
from datamuse import DatamuseAPI


class LandBot(discord.Client):
    """Bot implementation."""

    TEST_CMD = ("test", "тест", "т", "t")

    HELP_CMD = ("help", "introduce", "h", "?")

    RHYME_CMD = (
        "rh",
        "rhyme",
        "rhymes",
        "рими",
        "рима",
        "римички",
        "римичка",
        "римувай",
    )

    async def on_ready(self):
        """Ouput useful debugging information."""
        print(f"Bot logged in as {self.user}.")

    async def on_message(self, message):
        """Listen for messages starting with '!' and execute their commands."""
        if message.author == self.user:
            return

        msg = message.content.lower()
        msg_parts = msg.split()

        if len(msg_parts) < 1 or not msg[0] == "!":
            return

        print(f"Received command: {msg}")

        msg_parts[0] = msg_parts[0][1:]

        if msg_parts[0] in self.TEST_CMD:
            out_msg = self._test_command()
            await message.channel.send(out_msg)
            return

        if msg_parts[0] in self.RHYME_CMD:
            # 'Rhyme' command synthax:
            # !{command} {term} [{max_rhymes}]
            term = msg_parts[1]
            max_rhymes = 10 if len(msg_parts) < 3 else int(msg_parts[2])

            out_msg = self._rhyme_command(term, max_rhymes)
            await message.channel.send(out_msg)
            return

        if msg_parts[0] in self.HELP_CMD:
            out_msg = self._help_command()
            await message.channel.send(out_msg)
            return

    def _rhyme_command(self, term, max_rhymes=10):
        if re.search("[а-яА-Я]", term):
            # when cyrillic, use rimichka.com
            api = RimichkaAPI()
            rhymeslist = api.fetch_rhymes(term)
            print(f"Fetched {len(rhymeslist)} rhymes for {term}")
        else:
            # when latin, use datamuse.com
            api = DatamuseAPI()
            rhymeslist = api.fetch_rhymes(term)
            print(f"Fetched {len(rhymeslist)} rhymes for {term}")
            if not rhymeslist:  # possible "маймуница", try Bulgarian rhyme
                cyrillic = transliterate.translit(term, "bg")
                api = RimichkaAPI()
                rhymeslist = api.fetch_rhymes(cyrillic)
                print(f"Fetched {len(rhymeslist)} rhymes for {cyrillic}")

        if not rhymeslist:
            return f"What is *{term}*? I can't rhyme it."

        rhymeslist = rhymeslist[:max_rhymes]
        rows = [f"> {rhyme}" for rhyme in rhymeslist]
        out_msg = "\n".join(rows)
        return out_msg

    def _help_command(self):
        return """Hello! LandBot here. I serve the Landcore community.
You can write commands starting with '!' and I shall execute them.
Here are a few examples:
`!rhyme robot`
This will fetch the top 10 rhymes for the word 'robot'.
`!rhyme robot 22`
This will fetch the top 22 rhymes for the word 'robot'.
`!римувай кон`
This will fetch the top 10 rhymes for the word 'кон'.
`!test`
This just outputs a test message that shows that I'm online and the best.
`!help`
This will write the things you are reading right now.
My creator told me that I am gonna be learning new commands soon so stay tuned.
May the Bafta be with you!
"""

    def _test_command(self):
        # TODO: Choose a random message everytime.
        return "Test? Why not.\nI am the best bot."


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
