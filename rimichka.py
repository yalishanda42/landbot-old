"""Rimichka API service."""

import requests


class RimichkaAPI:
    """Implementations for the https://rimichka.com API."""

    BASE = "http://rimichka.com"

    def fetch_rhymes(self, word):
        """Return a list with rhymes for a given word."""
        try:
            response = requests.get(f"{self.BASE}/?word={word}&json=1").json()
            response.raise_for_status()
            response.sort(key=lambda d: d["pri"], reverse=True)
        except Exception:
            response = []

        return [d["wrd"] for d in response]


if __name__ == "__main__":
    # Test
    api = RimichkaAPI()
    rhymes = api.fetch_rhymes("кон")
    print(rhymes)
