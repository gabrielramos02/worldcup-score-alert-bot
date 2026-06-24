from datetime import datetime
import json

import aiohttp

from database.manager import (
    Live_Match,
    Team,
    add_team,
    get_subscription,
    get_team,
    get_teams,
)

BASE_URL_CORE = "https://sports.core.api.espn.com/v2/sports/soccer/"
BASE_URL_SITE = "https://site.api.espn.com/apis/site/v2/sports/soccer/"


async def get_teams_list() -> list[Team] | None:
    url = f"{BASE_URL_CORE}leagues/fifa.world/seasons/2026/teams"
    team_list = await get_teams()
    if len(team_list) == 48:
        return team_list

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            html: str | None = await response.text()
            serialized = json.loads(html)
            pages = serialized.get("pageCount", 1)
            for page in range(1, pages + 1):
                url = (
                    f"{BASE_URL_CORE}leagues/fifa.world/seasons/2026/teams?page={page}"
                )
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
                        await add_team(
                            team_id=team["id"],
                            team_name=team["displayName"],
                            logo_url=team["logos"][0]["href"],
                        )
                        team_list.append(
                            Team(
                                id=team["id"],
                                team_name=team["displayName"],
                                logo_url=team["logos"][0]["href"],
                            )
                        )
            print(f"Total teams found: {len(team_list)}")
            return team_list


async def get_from_url(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            html: str | None = await response.text()
            serialized = json.loads(html)
            return serialized


async def get_team_info(team_id: str) -> Team | None:
    url = f"{BASE_URL_CORE}leagues/fifa.world/seasons/2026/teams/{team_id}"
    team = await get_team(int(team_id))
    if team:
        return team
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html: str | None = await response.text()
            serialized = json.loads(html)
            if "id" in serialized:
                await add_team(
                    team_id=serialized["id"],
                    team_name=serialized["displayName"],
                    logo_url=serialized["logos"][0]["href"],
                )
                return Team(
                    id=serialized["id"],
                    team_name=serialized["displayName"],
                    logo_url=serialized["logos"][0]["href"],
                )


## TODO: Add Goal Scorers, Match Events, and other match details
async def get_matches_from_date(date: datetime) -> list[dict[str, str]]:
    url = f"{BASE_URL_SITE}fifa.world/scoreboard?dates={date.strftime('%Y%m%d')}"
    matches: list[dict[str, str]] = []

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html: str | None = await response.text()
            if html:
                serialized = json.loads(html)
                events = serialized.get("events", [])
                for event in events:
                    event_date = event.get("date", "")
                    event_completed = (
                        event.get("status", {}).get("type", {}).get("completed", False)
                    )
                    if event_date and not event_completed:
                        event_date = datetime.fromisoformat(event_date)
                        if event_date.date() != date.date():
                            continue
                    match_id = event.get("id", "")
                    home_team = (
                        event.get("competitions", [{}])[0]
                        .get("competitors", [{}])[0]
                        .get("team", {})
                        .get("displayName", "")
                    )
                    home_team_id = (
                        event.get("competitions", [{}])[0]
                        .get("competitors", [{}])[0]
                        .get("team", {})
                        .get("id", "")
                    )
                    away_team = (
                        event.get("competitions", [{}])[0]
                        .get("competitors", [{}])[1]
                        .get("team", {})
                        .get("displayName", "")
                    )
                    away_team_id = (
                        event.get("competitions", [{}])[0]
                        .get("competitors", [{}])[1]
                        .get("team", {})
                        .get("id", "")
                    )
                    home_score = (
                        event.get("competitions", [{}])[0]
                        .get("competitors", [{}])[0]
                        .get("score", "")
                    )
                    away_score = (
                        event.get("competitions", [{}])[0]
                        .get("competitors", [{}])[1]
                        .get("score", "")
                    )
                    date_time = event.get("date", "")
                    date_time = datetime.fromisoformat(date_time) if date_time else None
                    is_live = (
                        event.get("status", {}).get("type", {}).get("state", "") == "in"
                    )
                    matches.append(
                        {
                            "match_id": match_id,
                            "home_team": home_team,
                            "home_team_id": home_team_id,
                            "away_team": away_team,
                            "away_team_id": away_team_id,
                            "home_score": home_score,
                            "away_score": away_score,
                            "date_time": (
                                date_time.strftime("%d-%m-%Y %H:%M")
                                if date_time
                                else ""
                            ),
                            "is_live": is_live,
                        }
                    )
            return matches

live_matches_state: list[Live_Match] = []


async def get_live_matches() -> list[Live_Match]:
    url = f"{BASE_URL_SITE}fifa.world/scoreboard"
    LIVE_MATCHES: list[Live_Match] = []

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html: str | None = await response.text()
            if html:
                serialized = json.loads(html)
                events = serialized.get("events", [])
                for event in events:
                    is_live = (
                        event.get("status", {}).get("type", {}).get("state", "") == "in"
                    )
                    if not is_live:
                        continue
                    match_id = event.get("id", "")
                    home_team_id = (
                        event.get("competitions", [{}])[0]
                        .get("competitors", [{}])[0]
                        .get("team", {})
                        .get("id", "")
                    )
                    away_team_id = (
                        event.get("competitions", [{}])[0]
                        .get("competitors", [{}])[1]
                        .get("team", {})
                        .get("id", "")
                    )
                    home_score = (
                        event.get("competitions", [{}])[0]
                        .get("competitors", [{}])[0]
                        .get("score", "")
                    )
                    away_score = (
                        event.get("competitions", [{}])[0]
                        .get("competitors", [{}])[1]
                        .get("score", "")
                    )
                    clock_time = (
                        event.get("competitions", [{}])[0]
                        .get("status", {})
                        .get("displayClock", "")
                    )
                    is_live = (
                        event.get("status", {}).get("type", {}).get("state", "") == "in"
                    )
                    LIVE_MATCHES.append(
                        Live_Match(
                            match_id=match_id,
                            home_team_id=home_team_id,
                            away_team_id=away_team_id,
                            home_score=int(home_score) if home_score else 0,
                            away_score=int(away_score) if away_score else 0,
                            clock_time=clock_time if clock_time else "0'",
                            is_live=is_live,
                        )
                    )
            return LIVE_MATCHES
