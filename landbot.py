#!python3

"""LandBot - Discord chatbot serving the landcore community.

(c) 2020 Yalishanda.
"""

import asyncio
from typing import Optional
import discord
import logging
import re
from urllib.error import HTTPError
import transliterate
import os
from datetime import datetime
from pytz import timezone
import random
from dotenv import load_dotenv
from pytube import YouTube
from random import shuffle

from rimichka import RimichkaAPI
from datamuse import DatamuseAPI
from songs import LandcoreSongs

class LandBot(discord.Client):
    """Bot implementation."""

    # Properties

    voice_channel_id: Optional[int] = None
    songs_channel_id: Optional[int] = None

    # Constants

    COMMAND_START_SYMBOL = "."

    _TEST_CMD = ("test", "t", ".", "ping", "pong")

    _HELP_CMD = ("help", "introduce", "h", "?", "pomosht")

    _RHYME_CMD = (
        "rh",
        "rhyme",
        "rhymes",
        "rimi",
        "rima",
        "rimichki",
        "rimichka",
        "rimuvay",
    )

    _LINK_CMD = (
        "l",
        "s",
        "yt",
        "link",
        "song",
        "pesen",
        "youtube",
        "pozdrav",
        "greetings",
        "greet",
    )

    _WELCOME_MESSAGES = (
        "И ето пак във ~~вратата~~ сървъра влезе {0}",
        "Раз, два, три, четири... айде пет\n"
        "В сървъра влезе {0}, пожелавам им късмет",
        "{0} стиска ви здраво ръката",
        "Схема 1, схема 2, при {0} всичко е добре."
    )

    _WELCOME_USER_DM = """Добре дошъл в сървъра! Аз съм ландкор бота.
Само да знаеш, че мога изпълявам команди, започващи с точка.
Може да пробваш тука .help за повече информация."""

    # Overrides

    async def on_ready(self):
        """Client is connected."""
        print(f"Bot logged in as {self.user}.")
        await self._play_landcore_radio()

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
        msg_parts[0] = transliterate.translit(msg_parts[0],
                                              "bg",
                                              reversed=True)

        if "bafta" in msg or "бафта" in msg:
            await message.channel.send("*hahaa*")

        if len(msg_parts) < 1 or not msg[0] == self.COMMAND_START_SYMBOL:
            return

        print(f"Received command: {msg}")

        msg_parts[0] = msg_parts[0][1:]

        out_msg = ""

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

        elif msg_parts[0] in self._LINK_CMD and len(msg_parts) >= 2:
            out_msg = self._link_command(" ".join(msg_parts[1:]))

        elif msg_parts[0] in self._LINK_CMD and len(msg_parts) == 1:
            out_msg = self._random_song_cmd()

        if not out_msg:
            return

        await message.channel.send(out_msg)
        return

    # Public methods

    async def random_song_of_the_day(self):
        """Send a message with a random song of the day."""
        if not self.songs_channel_id: return

        songurl = random.choice(LandcoreSongs.URLS)
        message = f"Random song of the day: {songurl}"

        await self.get_channel(self.songs_channel_id).send(message)


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

Повече инфо винаги има тук: https://allexks.github.io/landbot/.
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
        return random.choice(LandcoreSongs.QUOTES)

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

    # Helper methods

    async def _play_landcore_radio(self):
        if not self.voice_channel_id: return
        channel = [c for c in self.guilds[0].channels if c.id == self.voice_channel_id][0]

        print("Downloading song data...")

        songlist = []
        try:
            songlist = [
                YouTube(link)
                for link in LandcoreSongs.URLS
            ]
        except HTTPError:
            print("Caught HTTPException, retrying...")
            await self._play_landcore_radio()
            return # fml

        activity = discord.Activity()
        activity.type = discord.ActivityType.listening
        activity.name = "landcore"
        await self.change_presence(activity=activity)

        print(f"Connecting to channel {channel}...")
        player = await channel.connect()
        self.songlist = songlist
        self.player = player
        if songlist:
            self._play_song_increment_count(0)
        else:
            print("No songs to play!")

    def _play_song_increment_count(self, i):
        if not self.player or not self.songlist: return

        if i >= len(self.songlist):
            i = 0

        if i == 0:
            shuffle(self.songlist)

        songdata = self.songlist[i]
        try:
            audio_url = songdata.streams.filter(only_audio=True).order_by("abr").first().url
            print(f"Playing {songdata.title}...")

            self.player.play(
                discord.FFmpegPCMAudio(audio_url),
                after=lambda e: self._play_song_increment_count(i+1)
            )
        except HTTPError:
            print(f"HTTPError received, skipping song {songdata.watch_url}")
            self._play_song_increment_count(i+1)



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


async def random_song_of_the_day_timer(bot):
    await bot.wait_until_ready()

    while True:
        now = datetime.now(timezone("Europe/Sofia"))
        if now.hour == 0 and now.minute == 0 and now.second == 0:
            print("Sending song of the day.")
            await bot.random_song_of_the_day()

        await asyncio.sleep(1)


if __name__ == "__main__":
    _setup_logger()

    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    voice_channel_id = os.getenv("VOICE_CHANNEL_ID")
    songs_channel_id = os.getenv("SONGS_CHANNEL_ID")

    client = LandBot()
    client.voice_channel_id = int(voice_channel_id) if voice_channel_id else None
    client.songs_channel_id = int(songs_channel_id) if songs_channel_id else None
    client.loop.create_task(random_song_of_the_day_timer(client))
    client.run(token)
