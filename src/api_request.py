import json
from typing import Any

import aiohttp

from database.manager import Team, add_team, get_team, get_teams

BASE_URL = "https://sports.core.api.espn.com/v2/sports/soccer/"


async def get_teams_list() -> list[Team] | None:
    url = f"{BASE_URL}leagues/fifa.world/seasons/2026/teams"
    team_list = await get_teams()
    if team_list:
        return team_list

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            html: str | None = await response.text()
            serialized = json.loads(html)
            items = serialized.get("items", [{"$ref", ""}])
            if type(items) is not list:
                raise ValueError("Items is not a list")

            for item in items:
                if type(item) is not dict:
                    raise ValueError("Item is not a dict")
                if "$ref" not in item:
                    raise ValueError("Item does not have a name")
                if type(item["$ref"]) is not str:
                    raise ValueError("Item name is not a string")
                team = await get_from_url(item["$ref"])
                await add_team(team_id=team["id"], team_name=team["displayName"], logo_url=team["logos"][0]["href"])
                team_list.append(Team(id=team["id"], team_name=team["displayName"], logo_url=team["logos"][0]["href"]))
            return team_list


async def get_from_url(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            html: str | None = await response.text()
            serialized = json.loads(html)
            return serialized

async def get_team_info(team_id: str) -> Team | None:
    url = f"{BASE_URL}leagues/fifa.world/seasons/2026/teams/{team_id}"
    team = await get_team(int(team_id))
    if team:
        return team
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html: str | None = await response.text()
            serialized = json.loads(html)
            if "id" in serialized:
                await add_team(team_id=serialized["id"], team_name=serialized["displayName"], logo_url=serialized["logos"][0]["href"])
                return Team(id=serialized["id"], team_name=serialized["displayName"], logo_url=serialized["logos"][0]["href"])
