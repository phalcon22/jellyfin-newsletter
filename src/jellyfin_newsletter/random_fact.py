import logging
import time

import argostranslate.package
import argostranslate.translate
import requests

logger = logging.getLogger(__name__)


def random_fact() -> str:
    resp = requests.get(
        url="https://uselessfacts.jsph.pl" + "/api/v2/facts/random",
        timeout=10,
    )

    return resp.json()["text"]


def propose_random_fact(lang: str) -> str:

    argostranslate.package.update_package_index()
    packages = argostranslate.package.get_available_packages()
    package = next(p for p in packages if p.from_code == "en" and p.to_code == lang)
    argostranslate.package.install_from_path(package.download())
    accepted = False
    fix_awaiting = False
    time.sleep(0.5)
    while not accepted:
        if not fix_awaiting:
            fact_en = random_fact()
            fact_fr = argostranslate.translate.translate(q=fact_en, from_code="en", to_code=lang)
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
