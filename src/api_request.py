import json
from typing import Any

import aiohttp

BASE_URL = "https://sports.core.api.espn.com/v2/sports/soccer/"


async def get_teams_list() -> list[dict[str, str]]:
    url = f"{BASE_URL}leagues/fifa.world/seasons/2026/teams"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            html: str | None = await response.text()
            serialized = json.loads(html)
            items = serialized.get("items", [{"$ref", ""}])
            if type(items) is not list:
                raise ValueError("Items is not a list")

            team_list: list[dict[str, Any]] = []

            for item in items:
                if type(item) is not dict:
                    raise ValueError("Item is not a dict")
                if "$ref" not in item:
                    raise ValueError("Item does not have a name")
                if type(item["$ref"]) is not str:
                    raise ValueError("Item name is not a string")
                team = await get_from_url(item["$ref"])
                team_list.append(team)
            return team_list


async def get_from_url(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            html: str | None = await response.text()
            serialized = json.loads(html)
            return serialized

async def get_team_info(team_id: str) -> dict[str, Any]:
    url = f"{BASE_URL}leagues/fifa.world/seasons/2026/teams/{team_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html: str | None = await response.text()
            serialized = json.loads(html)
            return serialized
