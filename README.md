# LandBot
Yes. A Landcore chatbot.

## Commands

### Rhyme

Gives a list of rhymes for a given word (supports Bulgarian words as well).

* Command variations

    * `!rhyme`
    * `!rhymes`
    * `!rh`
    * `!рими`
    * `!рима`
    * `!римички`
    * `!римичка`
    * `!римувай`


* Synthax

    `!{command} {term} [{max_rhymes}]`

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

### Test

* Command variations

    * `!test`
    * `!тест`
    * `!t`
    * `!т`


* Notes

    This command outputs a simple funny message for test purposes.

### Help

* Command variations

    * `!help`
    * `!introduce`
    * `!h`
    * `!?`
    * `!!`


* Notes

    This command outputs a message that briefly describes the purpose and capabilities of the bot.
