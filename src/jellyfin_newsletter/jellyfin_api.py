from datetime import datetime
from urllib.parse import urlencode

import requests

from jellyfin_newsletter.jellyfin_image_type import JellyfinImageType


class JellyfinAPI:
    def __init__(self, public_url: str, api_key: str, admin_user_id: str) -> None:
        self.public_url = public_url
        self.api_key = api_key
        self.admin_user_id = admin_user_id
        self.headers = {"X-Emby-Token": self.api_key}

    def get_server_name(self) -> str:
        response = requests.get(
            url=f"{self.public_url}/System/Configuration",
            headers=self.headers,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["ServerName"]

    def get_image_url(self, item_id: str, image_type: JellyfinImageType, blur_level: int) -> None:
        url = f"{self.public_url}/Items/{item_id}/Images/{image_type}"

        params = {
            "maxWidth": 300,
            "maxHeight": 450,
            "blur": blur_level
        }

        return f"{url}?{urlencode(params)}"

    def get_new_items(self, since_date: datetime) -> list[dict]:
        response = requests.get(
            url=f"{self.public_url}/Items",
            headers=self.headers,
            params={
                "SortBy": "DateCreated",
                "SortOrder": "Descending",
                "Filters": "IsNotFolder",
                "IncludeItemTypes": "Movie,Episode",
                "Recursive": "true",
                "Fields": "DateCreated,Path,ProviderIds,RunTimeTicks,ProductionYear",
                "Limit": 2000,
                "StartIndex": 0,
            },
            timeout=60,
        )
        response.raise_for_status()
        items = response.json().get("Items", [])

        return [item for item in items if "DateCreated" in item and item["DateCreated"] >= since_date.isoformat()]


    def get_season_info_dic(self, season_id: str) -> dict | None:
        response = requests.get(
            url=f"{self.public_url}/Users/{self.admin_user_id}/Items/{season_id}",
            headers=self.headers,
            params={"Fields": "ProductionYear,Name,IndexNumber,Overview"},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()


    def get_serie_info_dic(self, serie_id: str) -> dict | None:
        response = requests.get(
            url=f"{self.public_url}/Users/{self.admin_user_id}/Items/{serie_id}",
            headers=self.headers,
            params={"Fields": "ProductionYear,Name,IndexNumber,Overview"},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()


    def get_movie_info_dic(self, movie_id: str) -> dict | None:
        response = requests.get(
            url=f"{self.public_url}/Users/{self.admin_user_id}/Items/{movie_id}",
            headers=self.headers,
            params={"Fields": "ProductionYear,Overview,RunTimeTicks,Genres,DateCreated,ProviderIds"},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()


    def get_content_count(self) -> dict | None:
        response = requests.get(
            url=f"{self.public_url}/Items/Counts",
            headers=self.headers,
            params={"userId": self.admin_user_id},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()
