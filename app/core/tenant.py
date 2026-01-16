import json
from pathlib import Path
from typing import Dict, List, Optional

from flask import current_app, request

from app.core.progress import (
    mission_progress,
    mission_status,
    project_progress,
    project_status,
)

Mission = Dict[str, object]


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


def _load_missions_raw() -> Dict[str, Mission]:
    path = _missions_path()
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return {}

    if not isinstance(data, dict):
        return {}

    return data


def load_missions() -> Dict[str, Mission]:
    data = _load_missions_raw()
    return {slug: _normalize_mission(slug, mission) for slug, mission in data.items()}


def _write_missions(data: Dict[str, Mission]) -> None:
    path = _missions_path()
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, sort_keys=False)


def _slugify(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")


def _normalize_project(project: Dict[str, object]) -> Dict[str, object]:
    payload = dict(project)
    title = payload.get("title", "")
    if isinstance(title, str) and not payload.get("id"):
        payload["id"] = _slugify(title)

    status = project_status(payload)
    progress, done_tasks, total_tasks = project_progress(payload)
    payload["status"] = status
    payload["progress"] = progress
    payload["tasks_done"] = done_tasks
    payload["tasks_total"] = total_tasks
    return payload


def _normalize_mission(slug: str, mission: Dict[str, object]) -> Mission:
    payload = dict(mission)
    payload["slug"] = slug
    projects = payload.get("projects", [])
    if isinstance(projects, list):
        normalized_projects = [
            _normalize_project(project) for project in projects if isinstance(project, dict)
        ]
    else:
        normalized_projects = []

    payload["projects"] = normalized_projects
    payload["status"] = mission_status(normalized_projects)
    payload["progress"] = mission_progress(normalized_projects)
    return payload


def get_mission(slug: str) -> Optional[Mission]:
    missions = load_missions()
    mission = missions.get(slug)
    if not mission:
        return None
    return dict(mission)


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


def update_mission_meeting_link(slug: str, meeting_link: str) -> bool:
    missions = _load_missions_raw()
    mission = missions.get(slug)
    if not mission:
        return False
    mission["meeting_link"] = meeting_link
    _write_missions(missions)
    return True


def update_project_meeting_link(slug: str, project_id: str, meeting_link: str) -> bool:
    missions = _load_missions_raw()
    mission = missions.get(slug)
    if not mission:
        return False
    projects = mission.get("projects", [])
    if not isinstance(projects, list):
        return False
    updated = False
    for project in projects:
        if isinstance(project, dict) and project.get("id") == project_id:
            project["meeting_link"] = meeting_link
            updated = True
            break
    if not updated:
        return False
    mission["projects"] = projects
    _write_missions(missions)
    return True
