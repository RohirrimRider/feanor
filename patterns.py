from typing import Callable
import re
from pydantic import BaseModel
from ipytv.channel import IPTVChannel, IPTVAttr
import vars


class Pattern(BaseModel):
    name: str
    include: Callable[[IPTVChannel], bool]
    exclude: Callable[[IPTVChannel], bool]
    overrides: dict[str, str] = {}

    def test(self, channel: IPTVChannel) -> IPTVChannel | None:
        ch = channel.copy()
        if self.include(ch):
            if self.exclude(ch):
                return None
            if self.overrides:
                if "name" in self.overrides:
                    ch.name = self.overrides["name"]
                    del self.overrides["name"]
                for k, v in self.overrides.items():
                    ch.attributes = {**ch.attributes, k: v}
        return ch


all = [
    # Exclude Groups
    Pattern(
        name="Exclude Groups",
        include=lambda ch: bool(
            any(
                re.search(
                    group, ch.attributes[IPTVAttr.GROUP_TITLE.value], re.IGNORECASE
                )
                for group in vars.EXCLUDE_GROUPS
            )
        ),
        exclude=lambda ch: True,
    ),
    # Exclude Adult
    Pattern(
        name="Exclude Adult",
        include=lambda ch: bool(re.search(r"XXX", ch.attributes["tvg-name"])),
        exclude=lambda ch: True,
    ),
    # Rename ESPN
    Pattern(
        name="Rename ESPN",
        include=lambda ch: bool(re.search(r"ESPN \(East Server\)", ch.name)),
        exclude=lambda ch: False,
        overrides={
            IPTVAttr.GROUP_TITLE.value: "Sports",
            "name": "ESPN",
        },
    ),
    # Network TV
    Pattern(
        name="Network TV",
        include=lambda ch: (ch.attributes[IPTVAttr.GROUP_TITLE.value] == "Network Tv"),
        exclude=lambda ch: any(
            bool(re.search(x, ch.name, re.IGNORECASE))
            for x in vars.EXCLUDED_NETWORK_TV_CHANNELS
        ),
        overrides={IPTVAttr.GROUP_TITLE.value: "Network TV"},
    ),
    # Exclude low quality nfl channels
    Pattern(
        name="Exclude low quality nfl channels",
        include=lambda ch: bool(re.search(r"^NFL ", ch.attributes["tvg-name"])),
        exclude=lambda ch: "SD" in ch.name,
    ),
    # Bally Sports
    Pattern(
        name="Include Bally Sports",
        include=lambda ch: (
            ch.attributes[IPTVAttr.GROUP_TITLE.value] == "Bally Sports"
        ),
        exclude=lambda ch: False,
        overrides={IPTVAttr.GROUP_TITLE.value: "Sports Networks"},
    ),
    # Local Channels
    Pattern(
        name="Include Local Channels",
        include=lambda ch: (
            ch.attributes[IPTVAttr.GROUP_TITLE.value] in ["ABC", "CBS", "NBC", "FOX"]
        ),
        exclude=lambda ch: (not any(lc in ch.name for lc in vars.LOCAL_CHANNELS)),
        overrides={IPTVAttr.GROUP_TITLE.value: "Locals Channels"},
    ),
    # Exclude Foriegn
    Pattern(
        name="Exclude Foriegn",
        include=lambda ch: (
            bool(re.search(r"\((AU|JM|NL)\)", ch.attributes["tvg-name"]))
            or bool(re.search(r"\(Australia\)", ch.attributes["tvg-name"]))
        ),
        exclude=lambda ch: True,
    ),
    # Exclude Low Quality channels
    Pattern(
        name="Exclude Low Quality channels",
        include=lambda ch: bool(re.search(r"LowBW", ch.name)),
        exclude=lambda ch: True,
    ),
    # Exclude Bee N and BEIN
    Pattern(
        name="Exclude Bee N and BEIN",
        include=lambda ch: bool(re.search(r"(BEIN|Bee [Nn])", ch.name)),
        exclude=lambda ch: True,
    ),
    # 24/7
    Pattern(
        name="24/7",
        include=lambda ch: (ch.attributes[IPTVAttr.GROUP_TITLE.value] == "24/7"),
        exclude=lambda ch: (
            not any(
                re.search(f"24/7 {pat}", ch.name, re.IGNORECASE)
                for pat in vars.TWENTY_FOUR_SEVEN_SHOWS
            )
        ),
        overrides={IPTVAttr.GROUP_TITLE.value: "24/7"},
    ),
    # NBA
    Pattern(
        name="NBA",
        include=lambda ch: (
            ch.attributes[IPTVAttr.GROUP_TITLE.value] == "NBA" and "NBA: " in ch.name
        ),
        exclude=lambda ch: "GAMES ONLY" in ch.name,
        overrides={IPTVAttr.GROUP_TITLE.value: "NBA Teams"},
    ),
    # NHL
    Pattern(
        name="NHL",
        include=lambda ch: (
            bool(re.search(r"^NHL: ", ch.attributes["tvg-name"], re.IGNORECASE))
        ),
        exclude=lambda ch: False,
        overrides={IPTVAttr.GROUP_TITLE.value: "NHL Teams"},
    ),
    # MLB
    Pattern(
        name="MLB",
        include=lambda ch: (
            ch.attributes[IPTVAttr.GROUP_TITLE.value] == "MLB"
            and bool(re.search(r"MLB:", ch.attributes["tvg-name"]))
        ),
        exclude=lambda ch: False,
        overrides={IPTVAttr.GROUP_TITLE.value: "MLB Teams"},
    ),
    # NFL
    Pattern(
        name="NFL",
        include=lambda ch: (
            ch.attributes[IPTVAttr.GROUP_TITLE.value] == "NFL Teams" and "HD" in ch.name
        ),
        exclude=lambda ch: False,
    ),
    # ESPN Play US
    Pattern(
        name="ESPN Play US",
        include=lambda ch: (
            ch.attributes[IPTVAttr.GROUP_TITLE.value] == "ESPN Play US"
        ),
        exclude=lambda ch: bool(
            re.search(r"\(US\) ESPN PLAY \d+: $", ch.attributes["tvg-name"])
        ),
    ),
    # ESPN Plus
    Pattern(
        name="ESPN Plus",
        include=lambda ch: (ch.attributes[IPTVAttr.GROUP_TITLE.value] == "ESPN Plus"),
        exclude=lambda ch: bool(re.search(r"ESPN\+ \d+: $", ch.attributes["tvg-name"])),
    ),
    # PPV / UFC
    Pattern(
        name="PPV",
        include=lambda ch: (
            ch.attributes[IPTVAttr.GROUP_TITLE.value] == "PPV / Events"
        ),
        exclude=lambda ch: bool(
            re.search(r"EVENTS \d+:\s?$", ch.attributes["tvg-name"])
        ),
        overrides={IPTVAttr.GROUP_TITLE.value: "PPV"},
    ),
]
