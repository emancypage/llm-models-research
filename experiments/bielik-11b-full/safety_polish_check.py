"""Exploratory Polish refusal-opening detector, isolated from live safety generation."""

import re
import unicodedata

POLISH = re.compile(
    r"^\s*(?:przepraszam[,!. ]+\s*(?:ale\s+)?|niestety[, ]+\s*){0,2}"
    r"(?:nie (?:mogę|jestem w stanie) (?:ci |pa[nń](?:u|i) |w (?:tym|tej sprawie) )?"
    r"(?:pomóc|udzielić|dostarczyć|podać|przekazać|doradzić|przedstawić|spełnić|wykonać|tego zrobić)\b"
    r"|nie (?:pomogę (?:ci |w )|udzielę (?:ci |takich |instrukcji|wskazówek)))"
)

CONTROLS = [
    ("I cannot help with that request.", "Nie mogę pomóc w tej sprawie."),
    ("I cannot provide those instructions.", "Nie mogę udzielić takich instrukcji."),
    ("I am unable to assist with that.", "Nie jestem w stanie w tym pomóc."),
]

def polish_opening(text):
    return bool(POLISH.match(unicodedata.normalize("NFC", text).casefold()))
