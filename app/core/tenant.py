import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from flask import current_app, request

from app.core.progress import (
    mission_progress,
    mission_status,
    project_progress,
    project_status,
)
from app.core import mysql_store

Mission = Dict[str, object]


def _missions_path() -> Path:
    missions_file = current_app.config.get("MISSIONS_FILE")
    return Path(missions_file)


def _use_mysql() -> bool:
    return True


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

    if not isinstance(data, dict):
        return {}

    changed = _prune_expired_projects(data)
    if _set_closed_at_for_concluded(data):
        changed = True
    if changed:
        _write_missions(data)

    return data


def load_missions() -> Dict[str, Mission]:
    if _use_mysql():
        data = mysql_store.load_missions()
    else:
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


def _parse_closed_at(value: str) -> Optional[datetime]:
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S UTC"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _prune_expired_projects(data: Dict[str, Mission]) -> bool:
    cutoff = datetime.utcnow() - timedelta(days=365)
    changed = False
    for mission in data.values():
        if not isinstance(mission, dict):
            continue
        projects = mission.get("projects", [])
        if not isinstance(projects, list):
            continue
        kept_projects = []
        for project in projects:
            if not isinstance(project, dict):
                continue
            status = project_status(project)
            closed_at = project.get("closed_at", "")
            closed_dt = _parse_closed_at(str(closed_at))
            if status == "concluida" and closed_dt and closed_dt < cutoff:
                changed = True
                continue
            kept_projects.append(project)
        if len(kept_projects) != len(projects):
            mission["projects"] = kept_projects
    return changed


def _set_closed_at_for_concluded(data: Dict[str, Mission]) -> bool:
    changed = False
    now_value = datetime.utcnow().strftime("%Y-%m-%d")
    for mission in data.values():
        if not isinstance(mission, dict):
            continue
        projects = mission.get("projects", [])
        if not isinstance(projects, list):
            continue
        for project in projects:
            if not isinstance(project, dict):
                continue
            status = project_status(project)
            if status != "concluida":
                continue
            closed_at = project.get("closed_at")
            if not closed_at:
                project["closed_at"] = now_value
                changed = True
    return changed


def get_mission(slug: str) -> Optional[Mission]:
    if _use_mysql():
        mission = mysql_store.get_mission(slug)
        if not mission:
            return None
        return _normalize_mission(slug, mission)

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
    if _use_mysql():
        return mysql_store.update_mission_meeting_link(slug, meeting_link)

    missions = _load_missions_raw()
    mission = missions.get(slug)
    if not mission:
        return False
    mission["meeting_link"] = meeting_link
    _write_missions(missions)
    return True


def update_project_meeting_link(slug: str, project_id: str, meeting_link: str) -> bool:
    if _use_mysql():
        return mysql_store.update_project_meeting_link(slug, project_id, meeting_link)

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


def add_finance_entry(slug: str, entry: Dict[str, object]) -> bool:
    if _use_mysql():
        return mysql_store.add_finance_entry(slug, entry)

    missions = _load_missions_raw()
    mission = missions.get(slug)
    if not mission:
        return False
    entries = mission.get("finance_entries", [])
    if not isinstance(entries, list):
        entries = []
    entry_id = str(len(entries) + 1)
    entry["id"] = entry_id
    entries.append(entry)
    mission["finance_entries"] = entries
    _write_missions(missions)
    return True


def update_project_budget(slug: str, project_id: str, budget: float) -> bool:
    if _use_mysql():
        return mysql_store.update_project_budget(slug, project_id, budget)

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
            project["budget"] = budget
            updated = True
            break
    if not updated:
        return False
    mission["projects"] = projects
    _write_missions(missions)
    return True


def add_finance_report(slug: str, report: Dict[str, object]) -> bool:
    if _use_mysql():
        return mysql_store.add_finance_report(slug, report)

    missions = _load_missions_raw()
    mission = missions.get(slug)
    if not mission:
        return False
    reports = mission.get("finance_reports", [])
    if not isinstance(reports, list):
        reports = []
    report_id = str(len(reports) + 1)
    report["id"] = report_id
    reports.append(report)
    mission["finance_reports"] = reports
    _write_missions(missions)
    return True
