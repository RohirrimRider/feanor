from typing import Callable
import re
from pydantic import BaseModel
from ipytv.channel import IPTVChannel, IPTVAttr
from ipytv.playlist import loadf, M3UPlaylist


m3u_url = "playlist.m3u"
output_m3u_file = "filtered_playlist.m3u"


class Pattern(BaseModel):
    include: Callable[[IPTVChannel], bool]
    exclude: Callable[[IPTVChannel], bool]
    overrides: dict[str, str] = {}

    def test(self, channel: IPTVChannel) -> IPTVChannel | None:
        ch = channel.copy()
        if self.include(ch) and not self.exclude(ch):
            if self.overrides:
                for k, v in self.overrides.items():
                    ch.attributes = {**ch.attributes, k: v}
            return ch
        return None


SPORTS_CHANNELS = [
    "ESPN (East Server)",
    "ESPN2",
    "ESPN News",
    "ESPNU",
    "FOX Sports [12]",
    "(NFL|MLB|NHL) Network$",
    "NBA TV",
    "GOLF Channel",
    "AAC Network",
    "SEC Network",
    "^BIG TEN Network$",
    "CBS Sports Network",
    "MSG( 2)?",
    "MSGSN [12]$",
    "NBCSN$",
    "pac-12 network$",
    "TSN [1-5]",
    "sportsnet pittsburgh",
    "YES Network$",
]

patterns = [
    Pattern(
        include=lambda ch: (
            ch.attributes[IPTVAttr.GROUP_TITLE.value] == "Sports Networks"
            and any(re.match(pat, ch.name, re.IGNORECASE) for pat in SPORTS_CHANNELS)
        ),
        exclude=lambda ch: False,
        overrides={IPTVAttr.GROUP_TITLE.value: "Sports"},
    )
]


def test_filters(channel: IPTVChannel) -> IPTVChannel | None:
    for pattern in patterns:
        if ch := pattern.test(channel.copy()):
            return ch
    return None


def download_and_filter_m3u(
    url: str,
    patterns: list[Pattern],
    output_file: str,
) -> None:
    pl = loadf("playlist.m3u")
    new_pl = M3UPlaylist()

    for i, channel in enumerate(pl.get_channels()):
        if ch := test_filters(channel):
            print("Keeping", ch.name)
            new_pl.append_channel(ch)

    with open(output_file, "w") as f:
        f.writelines(new_pl.to_m3u_plus_playlist())


# Example usage

download_and_filter_m3u(m3u_url, patterns, output_m3u_file)
