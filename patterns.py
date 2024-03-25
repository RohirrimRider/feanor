import re
from typing import Any, Callable

from pydantic import BaseModel

import vars
from xtream import Category, LiveStream


class Pattern(BaseModel):
    name: str
    include: Callable[[LiveStream, Category], bool]
    exclude: Callable[[LiveStream, Category], bool]
    overrides: dict[str, Any] = {}

    def test(self, ch: LiveStream, category: Category) -> LiveStream | None:
        if self.include(ch, category):
            if self.exclude(ch, category):
                return None
            if self.overrides:
                ch = ch.copy(update=self.overrides)
        return ch


all = [
    # Exclude Groups
    Pattern(
        name="Exclude Groups",
        include=lambda _, cat: bool(
            any(re.search(group, cat.category_name, re.IGNORECASE) for group in vars.EXCLUDE_GROUPS)
        ),
        exclude=lambda _, __: True,
    ),
    # Exclude Adult
    Pattern(
        name="Exclude Adult",
        include=lambda ch, cat: bool(re.search(r"XXX", ch.name)),
        exclude=lambda ch, cat: True,
    ),
    # Rename ESPN
    Pattern(
        name="Rename ESPN",
        include=lambda ch, cat: bool(re.search(r"ESPN \(East Server\)", ch.name)),
        exclude=lambda ch, cat: False,
        overrides={"name": "ESPN"},
    ),
    # Network TV
    Pattern(
        name="Network TV",
        include=lambda ch, cat: (cat.category_name == "Network Tv"),
        exclude=lambda ch, cat: any(
            bool(re.search(x, ch.name, re.IGNORECASE)) for x in vars.EXCLUDED_NETWORK_TV_CHANNELS
        ),
    ),
    # Exclude low quality nfl channels
    Pattern(
        name="Exclude low quality nfl channels",
        include=lambda ch, cat: bool(re.search(r"^NFL ", ch.name)),
        exclude=lambda ch, cat: "SD" in ch.name,
    ),
    # Bally Sports
    Pattern(
        name="Include Bally Sports",
        include=lambda ch, cat: (cat.category_name == "Bally Sports"),
        exclude=lambda ch, cat: False,
    ),
    # Local Channels
    Pattern(
        name="Include Local Channels",
        include=lambda ch, cat: (cat.category_name in ["ABC", "CBS", "NBC", "FOX"]),
        exclude=lambda ch, cat: (not any(lc in ch.name for lc in vars.LOCAL_CHANNELS)),
    ),
    # Exclude Foriegn
    Pattern(
        name="Exclude Foriegn",
        include=lambda ch, cat: (
            bool(re.search(r"\((AU|JM|NL)\)", ch.name))
            or bool(re.search(r"\(Australia\)", ch.name))
        ),
        exclude=lambda ch, cat: True,
    ),
    # Exclude Low Quality channels
    Pattern(
        name="Exclude Low Quality channels",
        include=lambda ch, cat: bool(re.search(r"LowBW", ch.name)),
        exclude=lambda ch, cat: True,
    ),
    # Exclude Bee N and BEIN
    Pattern(
        name="Exclude Bee N and BEIN",
        include=lambda ch, cat: bool(re.search(r"(BEIN|Bee [Nn])", ch.name)),
        exclude=lambda ch, cat: True,
    ),
    # 24/7
    Pattern(
        name="24/7",
        include=lambda ch, cat: (cat.category_name == "24/7"),
        exclude=lambda ch, cat: (
            not any(
                re.search(f"24/7 {pat}", ch.name, re.IGNORECASE)
                for pat in vars.TWENTY_FOUR_SEVEN_SHOWS
            )
        ),
    ),
    # NBA
    Pattern(
        name="NBA",
        include=lambda ch, cat: cat.category_name == "NBA",
        exclude=lambda ch, cat: "GAMES ONLY" in ch.name or not ch.name.startswith("NBA: "),
    ),
    # NHL
    Pattern(
        name="NHL",
        include=lambda ch, cat: (bool(re.search(r"^NHL: ", ch.name, re.IGNORECASE))),
        exclude=lambda ch, cat: ch.name.startswith("ECHL"),
    ),
    # MLB
    Pattern(
        name="MLB",
        include=lambda ch, cat: (cat.category_name == "MLB"),
        exclude=lambda ch, cat: not ch.name.startswith("MLB:"),
    ),
    # NFL
    Pattern(
        name="NFL",
        include=lambda ch, cat: cat.category_name == "NFL Teams",
        exclude=lambda ch, cat: "HD" not in ch.name,
    ),
    # ESPN Play US
    Pattern(
        name="ESPN Play US",
        include=lambda ch, cat: (cat.category_name == "ESPN Play US"),
        exclude=lambda ch, cat: bool(re.search(r"\(US\) ESPN PLAY \d+: $", ch.name)),
    ),
    # ESPN Plus
    Pattern(
        name="ESPN Plus",
        include=lambda ch, cat: (cat.category_name == "ESPN Plus"),
        exclude=lambda ch, cat: bool(re.search(r"ESPN\+ \d+: $", ch.name)),
    ),
    # PPV / UFC
    Pattern(
        name="PPV",
        include=lambda ch, cat: (cat.category_name == "PPV / Events"),
        exclude=lambda ch, cat: bool(re.search(r"EVENTS \d+:\s?$", ch.name)),
    ),
]
