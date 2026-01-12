import json
from pathlib import Path
from typing import Dict, List, Optional

from flask import current_app, request

Mission = Dict[str, str]


def _missions_path() -> Path:
    missions_file = current_app.config.get("MISSIONS_FILE")
    return Path(missions_file)


def _is_ip_address(host: str) -> bool:
    return host.replace(".", "").isdigit()


def _extract_subdomain(host: str) -> Optional[str]:
    host = host.split(":")[0]
    if not host or _is_ip_address(host):
        return None
    if "." not in host:
        return None
    return host.split(".")[0]


def load_missions() -> Dict[str, Mission]:
    path = _missions_path()
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return {}

    if isinstance(data, dict):
        return data
    return {}


def get_mission(slug: str) -> Optional[Mission]:
    missions = load_missions()
    mission = missions.get(slug)
    if not mission:
        return None
    payload = dict(mission)
    payload["slug"] = slug
    return payload


def list_missions() -> List[Mission]:
    missions = load_missions()
    payloads = []
    for slug, mission in missions.items():
        payload = dict(mission)
        payload["slug"] = slug
        payloads.append(payload)

    return sorted(payloads, key=lambda item: item.get("name", "").lower())


def resolve_mission(slug: Optional[str] = None) -> Optional[Mission]:
    if slug:
        return get_mission(slug)

    host = request.host or ""
    subdomain = _extract_subdomain(host)
    if not subdomain:
        return None

    return get_mission(subdomain)
