#!python3

"""LandBot - Discord chatbot serving the landcore community.

(c) 2020 Yalishanda.
"""

import discord
import logging
import re
import transliterate
import os
import random
from dotenv import load_dotenv

from rimichka import RimichkaAPI
from datamuse import DatamuseAPI
from songs import LandcoreSongs


class LandBot(discord.Client):
    """Bot implementation."""

    # Commands

    _TEST_CMD = ("test", "тест", "т", "t")

    _HELP_CMD = ("help", "introduce", "h", "?")

    _RHYME_CMD = (
        "rh",
        "rhyme",
        "rhymes",
        "рими",
        "рима",
        "римички",
        "римичка",
        "римувай",
    )

    _LINK_CMD = (
        "l",
        "s",
        "yt",
        "link",
        "song",
        "линк",
        "песен",
        "youtube",
    )

    # Overrides

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

        if msg_parts[0] in self._TEST_CMD:
            out_msg = self._test_command()

        elif msg_parts[0] in self._RHYME_CMD:
            # 'Rhyme' command synthax:
            # !{command} {term} [{max_rhymes}]
            term = msg_parts[1]
            max_rhymes = 10 if len(msg_parts) < 3 else int(msg_parts[2])
            out_msg = self._rhyme_command(term, max_rhymes)

        elif msg_parts[0] in self._HELP_CMD:
            out_msg = self._help_command()

        elif msg_parts[0] in self._LINK_CMD:
            out_msg = self._link_command(" ".join(msg_parts[1:]))

        await message.channel.send(out_msg)
        return

    # Command implementations

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
`!песен фми`
This will give you the link for the 'ФМИ' song video in YouTube.
`!link live`
This will give you links to all live landcore gigs in YouTube.
`!test`
This just outputs a test message that shows that I'm online and the best.
`!help`
This will write the things you are reading right now.
For more info always check https://github.com/allexks/landbot.
My creator told me that I am gonna be learning new commands soon so stay tuned.
May the Bafta be with you!
"""

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
            return "Е туй вече не мога да го изримувам." 

        rhymeslist = rhymeslist[:max_rhymes]
        rows = [f"> {rhyme}" for rhyme in rhymeslist]
        out_msg = "\n".join(rows)
        return out_msg

    def _test_command(self):
        return random.choice(LandcoreSongs.CITATIONS)

    def _link_command(self, name):
        full_match_index = None
        partial_match_indices = []

        if re.match("[а-яА-Я]", name):
            name = transliterate.translit(name, "bg", reversed=True)

        name = name.lower()

        for i, names_tuple in enumerate(LandcoreSongs.NAMES):
            if names_tuple[0] == name:
                full_match_index = i
                break

            if name in names_tuple[1:]:
                partial_match_indices.append(i)

        if full_match_index is not None:
            return LandcoreSongs.URLS[full_match_index]

        if not partial_match_indices:
            return "хм? пробвай пак"

        if len(partial_match_indices) == 1:
            return LandcoreSongs.URLS[partial_match_indices[0]]

        result = "Може би имахте предвид:\n"
        result += "\n".join("[{0}]({1})"
                            .format(LandcoreSongs.NAMES[i][0],
                                    LandcoreSongs.URLS[i])
                            for i in partial_match_indices)
        return result


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


def _retrieve_token(keyword="DISCORD_TOKEN"):
    """Get the access token that is located in the given file."""
    load_dotenv()
    return os.getenv(keyword)


if __name__ == "__main__":
    _setup_logger()

    client = LandBot()

    token = _retrieve_token()
    client.run(token)
