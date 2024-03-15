from typing import Annotated
import os
from ipytv.channel import IPTVChannel
from ipytv.playlist import M3UPlaylist, loadu, loadf
from fastapi import FastAPI, Query, Response
import patterns

app = FastAPI()

BASE_URL = os.getenv("BASE_URL", "")
TEST_FILE = os.getenv("TEST_FILE")


@app.get("/xmltv.php")
async def get_xmltv(
    username: str = Query(..., description="Username"),
    password: str = Query(..., description="Password"),
):
    url = f"{BASE_URL}/xmltv.php?username={username}&password={password}"
    pl = loadf(TEST_FILE) if TEST_FILE else loadu(url)
    new_pl = M3UPlaylist()

    for i, channel in enumerate(pl.get_channels()):
        if ch := test_filters(channel.copy()):
            new_pl.append_channel(ch)

    return Response("")


@app.get("/get.php")
async def get_channels(
    username: str = Query(..., description="Username"),
    password: str = Query(..., description="Password"),
    type: Annotated[str, Query(..., description="Type")] = "m3u_plus",
    output: Annotated[str, Query(..., description="Output")] = "ts",
):
    url = f"{BASE_URL}/get.php?username={username}&password={password}&type={type}&output={output}"
    pl = loadf(TEST_FILE) if TEST_FILE else loadu(url)
    new_pl = M3UPlaylist()

    for i, channel in enumerate(pl.get_channels()):
        if ch := test_filters(channel.copy()):
            new_pl.append_channel(ch)

    return Response(new_pl.to_m3u_plus_playlist(), media_type="application/x-mpegURL")


def test_filters(channel: IPTVChannel) -> IPTVChannel | None:
    ch = channel.copy()
    for pattern in patterns.all:
        ch = pattern.test(ch)
        if ch is None:
            print(
                f"Excluded {channel.attributes['tvg-name']} because of '{pattern.name}'"
            )
            return None
    return ch
