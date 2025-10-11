# Jellyfin Newsletter

<p align="center">
 <img src="https://img.shields.io/github/license/phalcon22/jellyfin-newsletter"/>
 <img src="https://img.shields.io/github/v/release/phalcon22/jellyfin-newsletter"/>
</p>

## How to use

How to generate the html:

```python
from pathlib import Path

import pendulum

from jellyfin_newsletter.newsletter_constructor import JellyfinNewsletter
from jellyfin_newsletter.random_fact import propose_random_fact

since_datetime = pendulum.now("Europe/Paris").subtract(days=7).at(hour=0, minute=0, second=0)

newsletter = JellyfinNewsletter(
    jellyfin_public_url=url_of_your_jellyfin_server,
    jellyfin_api_key=jellyfin_api_key,
    jellyfin_admin_user_id=user_id_of_an_admin,
    since_datetime=since_datetime,
    server_logo_url=url_of_your_logo,
    header_text=f"🍿 New content since {since_datetime.date()}",
    footer="The best platform ever",
    random_fact=propose_random_fact(lang="en"),
)
newsletter.fetch()

html = newsletter.to_html()
Path("email.html").write_text(html, encoding="utf-8")
```

How to send the html:

```python
from pathlib import Path

from jellyfin_newsletter.send_email import generate_mail_mime, send_email

html = Path("email.html").read_text(encoding="utf-8")

mime = generate_mail_mime(html, your_email_address, subject)
send_email(
    smtp_host=your_smtp_host,
    smtp_email=your_email_address,
    smtp_password=your_smtp_password,
    to=["user1@email.com", "user2@email.com"],
    mime=mime,
)
```

## What it looks like

<p align='center'>
    <img src='https://github.com/phalcon22/jellyfin-newsletter/blob/master/example.png?raw=true'/><br>
</p>
