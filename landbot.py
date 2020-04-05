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

    # Constants

    COMMAND_START_SYMBOL = "."

    _TEST_CMD = ("test", "тест", "т", "t", ".")

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
        "поздрав",
        "greetings",
        "greet",
    )

    _WELCOME_MESSAGES = (
        "И ето пак във ~~вратата~~ чата влезе {0}",
        "Раз, два, три, четири... айде пет\nВ чата влезе {0}, пожелавам им късмет",
        "{0} стиска ви здраво ръката",
    )

    _WELCOME_USER_DM = """Добре дошъл в сървъра! Аз съм ландкор бота.
Само да знаеш, че мога изпълявам команди, започващи \
с точка.
Може да пробваш .help за повече информация (това на лично, че да не спамя \
на другите)."""

    # Overrides

    async def on_ready(self):
        """Ouput useful debugging information."""
        print(f"Bot logged in as {self.user}.")

    async def on_member_join(self, member):
        """Handle a user joining the server."""
        print(f"User {member} joined the server!")

        if member.bot:
            return

        out_format = random.choice(self._WELCOME_MESSAGES)
        out_msg = out_format.format(f"**{member.name}**")
        for channel in member.guild.channels:
            if channel.name == 'general':
                await channel.send(out_msg)

        usr_msg = self._WELCOME_USER_DM
        await member.send(usr_msg)

    async def on_message(self, message):
        """Listen for patterns and execute commands."""
        if message.author == self.user:
            return

        msg = message.content.lower()
        msg_parts = msg.split()

        if "bafta" in msg or "бафта" in msg:
            await message.channel.send("*hahaa*")

        if len(msg_parts) < 1 or not msg[0] == self.COMMAND_START_SYMBOL:
            return

        print(f"Received command: {msg}")

        msg_parts[0] = msg_parts[0][1:]

        if msg_parts[0] in self._TEST_CMD:
            out_msg = self._test_command()

        elif msg_parts[0] in self._RHYME_CMD:
            # 'Rhyme' command synthax:
            # .{command} {term} [{max_rhymes}]
            term = msg_parts[1]
            max_rhymes = 10 if len(msg_parts) < 3 else int(msg_parts[2])
            out_msg = self._rhyme_command(term, max_rhymes)

        elif msg_parts[0] in self._HELP_CMD:
            out_msg = self._help_command()

        elif msg_parts[0] in self._LINK_CMD and len(msg_parts) == 2:
            out_msg = self._link_command(" ".join(msg_parts[1:]))

        elif msg_parts[0] in self._LINK_CMD and len(msg_parts) == 1:
            out_msg = self._random_song_cmd()

        await message.channel.send(out_msg)
        return

    # Command implementations

    def _help_command(self):
        return """И ето пак команда с '.' се задава.
LandBot-a я вижда и веднага отговаря.

Ето някои примери:
* `.rhyme robot`
Ще дам няколко рими на 'robot'.
* `.rhyme robot 22`
Ще дам най-много 22 рими на 'robot'.
* `.римувай кон`
Ще дам няколко рими на 'кон'.
* `.поздрав фми`
Ще пратя в чата песента 'ФМИ' (демек линк към YouTube видеото).
* `.link live`
Ще пратя всички лайв ландкор изгъзици.
* `.песен`
Ще пратя случайно-избрана песен.
* `.test`
Ще те разсмея. Може би. Нз. Ама при всеки случай ще разбереш дали съм онлайн.
* `.help`
Ще напиша това, което четеш сега.

Повече инфо винаги има тук: https://github.com/allexks/landbot.
Очаква се да мога да правя и още неща в бъдеще.
Приятно ландкориране.
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

    def _random_song_cmd(self):
        return random.choice(LandcoreSongs.URLS)


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
