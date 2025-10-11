from importlib import resources


def runtime_ticks_to_str(runtime_ticks: int) -> str:
    duration_minutes = runtime_ticks / 10_000_000 // 60
    hour = int(duration_minutes // 60)
    minute = int(duration_minutes % 60)

    if hour > 0:
        return f"{hour}h{minute:02}"
    return f"{minute:02} min"

def load_template(filename: str) -> bytes:
    return resources.files("jellyfin_newsletter.assets").joinpath(filename).read_text(encoding="utf-8")
