from typing import Any

import pendulum
from dateutil import parser

from jellyfin_newsletter.html_generation import newsletter_to_htmls
from jellyfin_newsletter.jellyfin_api import JellyfinAPI
from jellyfin_newsletter.jellyfin_image_type import JellyfinImageType
from jellyfin_newsletter.utils import runtime_ticks_to_str


class Episode:
    def __init__(self, info_dic: dict[str, Any]) -> None:
        self.item_id = info_dic["Id"]
        self.title = info_dic["Name"]
        self.runtime_ticks = info_dic["RunTimeTicks"]
        self.duration = runtime_ticks_to_str(info_dic["RunTimeTicks"])
        self.date = parser.parse(info_dic["PremiereDate"])
        self.year = self.date.year
        self.index_number = info_dic["IndexNumber"]


class Season:
    def __init__(self, season_id: str, api: JellyfinAPI) -> None:
        self.info_dic = api.get_season_info_dic(season_id)

        self.serie_id = self.info_dic["SeriesName"]
        self.item_id = season_id
        self.title = self.info_dic["Name"]
        self.date = parser.parse(self.info_dic["PremiereDate"])
        self.year = self.date.year
        self.index_number = self.info_dic["IndexNumber"]
        self.available_episode_count = self.info_dic["RecursiveItemCount"]
        self.episodes: dict[str, Episode] = {}

    def add_episode(self, info_dic: dict[str, Any]) -> None:
        episode = Episode(info_dic)

        if episode.item_id in self.episodes:
            msg = f"Episode appeared twice {episode.item_id}"
            raise Exception(msg)

        self.episodes[episode.item_id] = episode

    def get_min_episode(self) -> int:
        min_episode = 9999
        for episode in self.episodes.values():
            min_episode = min(min_episode, episode.index_number)

        return min_episode

    def get_max_episode(self) -> int:
        max_episode = -1
        for episode in self.episodes.values():
            max_episode = max(max_episode, episode.index_number)

        return max_episode

    def __str__(self) -> str:
        return f"{self.title} - {self.year} - {len(self.episodes)} episodes"

    def get_added_episode_count(self) -> int:
        return len(self.episodes)


class Serie:
    def __init__(self, serie_id: str, api: JellyfinAPI) -> None:
        self.info_dic = api.get_serie_info_dic(serie_id)

        self._api = api
        self.item_id: str = serie_id
        self.title: str = self.info_dic["Name"]
        self.images = {
            JellyfinImageType.PRIMARY: api.get_image_url(self.item_id, JellyfinImageType.PRIMARY, blur_level=0),
            JellyfinImageType.BACKDROP: api.get_image_url(self.item_id, JellyfinImageType.BACKDROP, blur_level=5),
        }
        self.date = parser.parse(self.info_dic["PremiereDate"])
        self.year = self.date.year
        self.available_season_count = self.info_dic["ChildCount"]
        self.available_episode_count = self.info_dic["RecursiveItemCount"]
        self.seasons: dict[str, Season] = {}

    def add_episode(self, info_dic: dict[str, Any]) -> None:
        season_id = info_dic["SeasonId"]

        if season_id not in self.seasons:
            self.seasons[season_id] = Season(season_id, self._api)

        self.seasons[season_id].add_episode(info_dic)
        self.seasons = dict(sorted(self.seasons.items(), key=lambda item: item[1].index_number))

    def get_average_episode_duration(self) -> str:
        episode_runtime_ticks = []
        for season in self.seasons.values():
            episode_runtime_ticks.extend([episode.runtime_ticks for episode in season.episodes.values()])

        return runtime_ticks_to_str(sum([runtime / len(episode_runtime_ticks) for runtime in episode_runtime_ticks]))

    def __str__(self) -> str:
        return f"{self.title} - {len(self.seasons)} seasons:\n" + "\n".join([str(season) for season in self.seasons.values()])

    def get_added_episode_count(self) -> int:
        return sum([season.get_added_episode_count() for season in self.seasons.values()])

    def is_new(self) -> bool:
        return self.get_added_episode_count() == self.available_episode_count


class Movie:
    def __init__(self, movie_id: str, api: JellyfinAPI) -> None:
        self.info_dic = api.get_movie_info_dic(movie_id)

        self.item_id = self.info_dic["Id"]
        self.title = self.info_dic["Name"]
        self.duration = runtime_ticks_to_str(self.info_dic["RunTimeTicks"])
        self.date = parser.parse(self.info_dic["PremiereDate"])
        self.year = self.date.year
        self.images = {
            JellyfinImageType.PRIMARY: api.get_image_url(self.item_id, JellyfinImageType.PRIMARY, blur_level=0),
            JellyfinImageType.BACKDROP: api.get_image_url(self.item_id, JellyfinImageType.BACKDROP, blur_level=5),
        }

    def __str__(self) -> str:
        return f"{self.title} - {self.year} - {self.duration}"


class JellyfinNewsletter:
    def __init__(
        self,
        jellyfin_public_url: str,
        jellyfin_api_key: str,
        jellyfin_admin_user_id: str,
        since_datetime: pendulum.DateTime,
        server_logo_url: str,
        header_text: str,
        footer: str,
        random_fact: str | None = None,
    ) -> None:
        self.api = JellyfinAPI(jellyfin_public_url, jellyfin_api_key, jellyfin_admin_user_id)

        self.movies: dict[str, Movie] = {}
        self.series: dict[str, Serie] = {}
        self.since_datetime = since_datetime
        self.random_fact = random_fact

        total_content_count = self.api.get_content_count()
        self.server_name = self.api.get_server_name()
        self.server_logo_url = server_logo_url
        self.header_text = header_text
        self.footer = footer
        self.total_movies_count = total_content_count["MovieCount"]
        self.total_series_count = total_content_count["SeriesCount"]
        self.total_episodes_count = total_content_count["EpisodeCount"]

    def fetch(self) -> None:
        for item in self.api.get_new_items(self.since_datetime):
            if item["Type"] == "Movie":
                self.add_movie(item)
            elif item["Type"] == "Episode":
                self.add_episode(item)
            else:
                msg = f"Unknown type: {item['Type']}"
                raise ValueError(msg)

    def add_movie(self, movie_info_dic: dict[str, Any]) -> None:
        movie = Movie(movie_info_dic["Id"], self.api)

        if movie.item_id in self.movies:
            msg = f"Movie appeared twice {movie.item_id}"
            raise Exception(msg)

        self.movies[movie.item_id] = movie

    def add_episode(self, info_dic: dict[str, Any]) -> None:
        serie_id = info_dic["SeriesId"]

        if serie_id not in self.series:
            self.series[serie_id] = Serie(serie_id, self.api)

        self.series[serie_id].add_episode(info_dic)

    def get_added_movie_count(self) -> int:
        return len(self.movies)

    def get_added_episode_count(self) -> int:
        return sum([serie.get_added_episode_count() for serie in self.series.values()])

    def get_added_serie_count(self) -> int:
        return len([serie for serie in self.series.values() if serie.is_new()])

    def __str__(self) -> str:
        return "\n".join([str(movie) for movie in self.movies.values()]) + "\n\n".join(
            [str(serie) for serie in self.series.values()]
        )

    def to_htmls(self) -> list[str]:
        return newsletter_to_htmls(self)
