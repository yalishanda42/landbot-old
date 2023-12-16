"""Datamuse.com API service."""

import requests


class DatamuseAPI:
    """Implementations for the Datamuse API."""

    BASE = "https://api.datamuse.com"

    def fetch_rhymes(self, word):
        """Return a list with rhymes for a given word."""
        try:
            response = requests.get(f"{self.BASE}/words?rel_rhy={word}").json()
            response.raise_for_status()
        except Exception:
            response = []

        return [d["word"] for d in response]


if __name__ == "__main__":
    # Test
    api = DatamuseAPI()
    rhymes = api.fetch_rhymes("englishman")
    print(rhymes)
