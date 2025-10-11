from __future__ import annotations

from typing import TYPE_CHECKING

from jellyfin_newsletter import utils
from jellyfin_newsletter.jellyfin_api import JellyfinImageType

if TYPE_CHECKING:
    from jellyfin_newsletter.newsletter_constructor import JellyfinNewsletter, Movie, Season, Serie

NEW_BADGES = {
    "series":  '<span class="info-badge" style="background:#ff9800;">New Series</span>',
    "season":  '<span class="info-badge" style="background:#9c27b0;">New Season</span>',
    "episode": '<span class="info-badge" style="background:#00bcd4;">New Episodes</span>',
}

def _movie_to_html(jellyfin_public_url: str, movie: Movie, template: str) -> str:
    return template.format(
        jellyfin_public_url=jellyfin_public_url,
        poster_image=movie.images[JellyfinImageType.PRIMARY],
        background_image=movie.images[JellyfinImageType.BACKDROP],
        title=movie.title,
        duration=movie.duration,
        year=movie.year,
        summary=""
    )


def _season_to_html(season: Season) -> str:
    template_season = utils.load_template("mail_template/body_season.html")

    min_episode = season.get_min_episode()
    max_episode = season.get_max_episode()
    episode_span = f"{min_episode}-{max_episode}" if min_episode != max_episode else min_episode
    return template_season.format(
        title=season.title,
        year=season.year,
        episode_span=episode_span
    )


def _serie_to_html(jellyfin_public_url: str, serie: Serie, template: str) -> str:
    body_seasons = "\n".join([_season_to_html(season) for season in serie.seasons.values()])

    badges = []
    if serie.available_episode_count == serie.get_added_episode_count():
        badges.append(NEW_BADGES["series"])

    else:
        for season in serie.seasons.values():
            if season.available_episode_count == season.get_added_episode_count():
                badges.append(NEW_BADGES["season"])
                break

    if len(badges) == 0:
        badges.append(NEW_BADGES["episode"])


    return template.format(
        jellyfin_public_url=jellyfin_public_url,
        poster_image=serie.images[JellyfinImageType.PRIMARY],
        background_image=serie.images[JellyfinImageType.BACKDROP],
        title=serie.title,
        badges="".join(badges),
        duration=serie.get_average_episode_duration(),
        year=serie.year,
        body_seasons=body_seasons,
        summary=""
    )


def newsletter_to_html(newsletter: JellyfinNewsletter) -> str:
    template = utils.load_template("mail_template/template.html")
    header = utils.load_template("mail_template/header.html")
    template_movie = utils.load_template("mail_template/body_movie.html")
    template_serie = utils.load_template("mail_template/body_serie.html")

    cards = []
    for item in newsletter.movies.values():
        html = _movie_to_html(newsletter.api.public_url, item, template_movie)
        cards.append(html)

    for item in newsletter.series.values():
        html = _serie_to_html(newsletter.api.public_url, item, template_serie)
        cards.append(html)

    nb_new_movies = newsletter.get_added_movie_count()
    nb_new_series = newsletter.get_added_serie_count()
    nb_new_episodes = newsletter.get_added_episode_count()

    return template.format(
        header=header,
        server_logo_url=newsletter.server_logo_url,
        jellyfin_public_url=newsletter.api.public_url,
        header_text=newsletter.header_text,
        nb_movies=newsletter.total_movies_count - nb_new_movies,
        nb_new_movies=nb_new_movies,
        nb_series=newsletter.total_series_count - nb_new_series,
        nb_new_series=nb_new_series,
        nb_episodes=newsletter.total_episodes_count - nb_new_episodes,
        nb_new_episodes=nb_new_episodes,
        random_fact=newsletter.random_fact,
        body="\n".join(cards),
        footer=newsletter.footer,
    )
