# LandBot
Yes. A Landcore chatbot.

## Commands

### Rhyme

Gives a list of rhymes for a given word (supports Bulgarian words as well).

* Command variations

    * `.rhyme`
    * `.rhymes`
    * `.rh`
    * `.рими`
    * `.рима`
    * `.римички`
    * `.римичка`
    * `.римувай`


* Syntax

    `.{command} {term} [{max_rhymes}]`

* Parameters

    * `term`

    The word to be rhymed.

    * `max_rhymes` (*Optional*)

    The maximum number of rhymes sent in the output. If not provided, the default is 10.

* Notes

    The command first determines whether `term` contains cyrillic letters.
    If it does, it uses rimichka.com as a rhyme provider.
    If it does not, it creates a request to datamuse.com and if the result is empty attempts to transliterate the `term` from latin to cyrillic and proceeds to make a request to rimichka.com.

    The results are ordered by precision descendingly and limited to a maximum of `max_rhymes`.

### Link

Get a YouTube link for a landcore song.

* Command variations

    * `.link`
    * `.линк`
    * `.song`
    * `.песен`
    * `.youtube`
    * `.l`
    * `.s`
    * `.yt`
    * `.поздрав`
    * `.greetings`
    * `.greet`


* Syntax

    `.{command} [{song_name}]`

* Parameters

    * `song_name` (*Optional*)

    The name of the song.
    If ommitted, a song is chosen at random.

* Notes

    This command tries to provide a YouTube video link for the given landcore song name. If the song name does match completely it searches the database for a partial match. If multiple possible results are present it proceeds to output all of them.

    If no song name is provided, a random song is outputted.


### Test

* Command variations

    * `.test`
    * `.тест`
    * `.t`
    * `.т`
    * `.ping`
    * `.пинг`
    * `.pong`
    * `.понг`
    * `..`


* Notes

    This command outputs a landcore quote for test purposes.

### Help

* Command variations

    * `.help`
    * `.introduce`
    * `.h`
    * `.?`


* Notes

    This command outputs a message that briefly describes the purpose and capabilities of the bot.
