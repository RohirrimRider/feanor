import os
import re
from typing import AsyncGenerator

import httpx
from fastapi import FastAPI, Query, Request
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse

import patterns
import vars
import xtream

categories: list[xtream.Category] = []

app = FastAPI()

BASE_URL = os.getenv("BASE_URL", "")
TEST_FILE = os.getenv("TEST_FILE")

proxy_client = httpx.AsyncClient(base_url=BASE_URL)

NONE_CATEGORY = xtream.Category(category_id="", category_name="", parent_id=0)


@app.get("/player_api.php")
async def player_api(
    request: Request,
    username: str = Query(..., description="Username"),
    password: str = Query(..., description="Password"),
    action: str = Query(..., description="Action"),
    category_id: str = Query("", description="Action"),
):
    match action:
        case "get_live_streams":
            return await get_live_streams(username, password, category_id)
        case "get_live_categories":
            return await get_live_categories(username, password)

    url = httpx.URL(path=request.url.path, query=request.url.query.encode("utf-8"))
    rp_req = proxy_client.build_request(
        request.method, url, headers=request.headers.raw, content=await request.body()
    )
    rp_resp = await proxy_client.send(rp_req, stream=True)
    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=rp_resp.headers,
        background=BackgroundTask(rp_resp.aclose),
    )


async def _reverse_proxy(request: Request):
    url = httpx.URL(path=request.url.path, query=request.url.query.encode("utf-8"))
    rp_req = proxy_client.build_request(
        request.method, url, headers=request.headers.raw, content=await request.body()
    )
    rp_resp = await proxy_client.send(rp_req, stream=True)
    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=rp_resp.headers,
        background=BackgroundTask(rp_resp.aclose),
    )


app.add_route(
    "/{path:path}",
    _reverse_proxy,
    methods=["GET", "OPTIONS", "HEAD"],
)


async def get_live_streams(
    username: str, password: str, category_id: str
) -> list[xtream.LiveStream]:
    categories = await get_all_live_categories(username, password)
    streames: list[xtream.LiveStream] = []
    async for stream in get_all_live_streams(username, password):
        if category_id and stream.category_id != category_id:
            continue
        if ch := test_filters(stream, categories):
            streames.append(ch)
    return streames


async def get_live_categories(username: str, password: str) -> list[xtream.Category]:
    return [
        category
        for category in await get_all_live_categories(username, password)
        if not any(
            re.search(group, category.category_name, re.IGNORECASE) for group in vars.EXCLUDE_GROUPS
        )
    ]


async def get_all_live_categories(username: str, password: str) -> list[xtream.Category]:
    params = {
        "username": username,
        "password": password,
        "action": "get_live_categories",
    }
    resp = await proxy_client.get("/player_api.php", params=params)
    resp.raise_for_status()
    raw_json = resp.json()
    return [xtream.Category.model_validate(x) for x in raw_json]


async def get_all_live_streams(
    username: str, password: str
) -> AsyncGenerator[xtream.LiveStream, None]:
    categories = await get_all_live_categories(username, password)
    params = {
        "username": username,
        "password": password,
        "action": "get_live_streams",
    }
    resp = await proxy_client.get("/player_api.php", params=params)
    resp.raise_for_status()
    raw_body = resp.json()
    for x in raw_body:
        x["category_name"] = next(
            (c.category_name for c in categories if c.category_id == x["category_id"]),
            "",
        )
        yield xtream.LiveStream.model_validate(x)


def test_filters(
    stream: xtream.LiveStream, categories: list[xtream.Category]
) -> xtream.LiveStream | None:
    for pattern in patterns.all:
        category = next((c for c in categories if c.category_id == stream.category_id), None)
        ch = pattern.test(stream, category or NONE_CATEGORY)
        if ch is None:
            return None
    return stream
