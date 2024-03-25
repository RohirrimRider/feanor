from typing import Annotated
import os
from ipytv.channel import IPTVChannel
from ipytv.playlist import M3UPlaylist, loadu, loadf
from fastapi import FastAPI, Query, Response, Request
import aiohttp
import patterns

app = FastAPI()

BASE_URL = os.getenv("BASE_URL", "")
TEST_FILE = os.getenv("TEST_FILE")


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


@app.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE"],
)
async def proxy(request: Request, full_path: str) -> Response:
    method = request.method
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)

    async with aiohttp.ClientSession() as session, session.request(
        method,
        f"{BASE_URL}/{full_path}",
        headers=headers,
        data=body,
        params=request.query_params,
    ) as resp:
        headers = resp.headers
        return Response(
            content=await resp.content.read(),
            headers=headers,
            status_code=resp.status,
        )


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
