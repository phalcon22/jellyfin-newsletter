import logging

import requests
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)


def random_fact(lang: str) -> tuple[str, str]:
    resp = requests.get(
        url="https://uselessfacts.jsph.pl" + "/api/v2/facts/random",
        timeout=10,
    )

    fact_en = resp.json()["text"]
    fact_translated = fact_en if lang == "en" else GoogleTranslator(source="en", target=lang).translate(fact_en)

    return fact_en, fact_translated


def propose_random_fact(lang: str) -> str:
    accepted = False
    fix_awaiting = False
    while not accepted:
        if not fix_awaiting:
            fact_en, fact_fr = random_fact(lang)
        fix_awaiting = False

        resp = input(f"Proposition:\n{fact_en}\n{fact_fr}\n\nDo you like it ? [Y]es, [N]o, [F]ix translation: ").lower()
        while resp not in ("y", "n", "f"):
            resp = input(f"{resp} not accepted, Do you like it ? [Y]es, [N]o, [F]ix translation: ")

        if resp == "y":
            accepted = True
        elif resp == "f":
            fact_fr = input("Enter fix: ")
            fix_awaiting = True

    return fact_fr
