import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from flask import current_app

from app.core.cache import cache_delete, cache_get, cache_set
from app.core.db import get_connection

Mission = Dict[str, object]


def _fetchone(cursor, query: str, params: tuple):
    cursor.execute(query, params)
    return cursor.fetchone()


def _fetchall(cursor, query: str, params: tuple):
    cursor.execute(query, params)
    return cursor.fetchall()


def _cleanup_projects(cursor) -> None:
    cutoff = datetime.utcnow().date() - timedelta(days=365)
    cursor.execute(
        """
        SELECT mission_id, project_key
        FROM mission_projects
        WHERE status = %s AND closed_at IS NOT NULL AND closed_at < %s
        """,
        ("concluida", cutoff),
    )
    expired = cursor.fetchall()
    for row in expired:
        cursor.execute(
            """
            DELETE FROM project_tasks
            WHERE mission_id = %s AND project_key = %s
            """,
            (row["mission_id"], row["project_key"]),
        )
        cursor.execute(
            """
            DELETE FROM finance_entries
            WHERE mission_id = %s AND project_key = %s
            """,
            (row["mission_id"], row["project_key"]),
        )
    cursor.execute(
        """
        DELETE FROM mission_projects
        WHERE status = %s AND closed_at IS NOT NULL AND closed_at < %s
        """,
        ("concluida", cutoff),
    )


def _ensure_closed_at(cursor) -> None:
    today = datetime.utcnow().date()
    cursor.execute(
        """
        UPDATE mission_projects
        SET closed_at = %s
        WHERE status = %s AND (closed_at IS NULL OR closed_at = '')
        """,
        (today, "concluida"),
    )


def load_missions() -> Dict[str, Mission]:
    cached = cache_get("missions:list")
    if isinstance(cached, dict):
        return cached

    with get_connection() as connection:
        if connection is None:
            return {}
        with connection.cursor() as cursor:
            _ensure_closed_at(cursor)
            _cleanup_projects(cursor)
            missions = _fetchall(cursor, "SELECT * FROM missions ORDER BY name", ())

    payload = {}
    for mission in missions:
        mission_data = _load_mission_by_id(mission["id"])
        if mission_data:
            payload[mission_data["slug"]] = mission_data
    cache_set(
        "missions:list",
        payload,
        current_app.config.get("REDIS_TTL_LIST", 120),
    )
    return payload


def get_mission(slug: str) -> Optional[Mission]:
    cached = cache_get(f"mission:{slug}")
    if isinstance(cached, dict):
        return cached

    with get_connection() as connection:
        if connection is None:
            return None
        with connection.cursor() as cursor:
            _ensure_closed_at(cursor)
            _cleanup_projects(cursor)
            mission = _fetchone(
                cursor,
                "SELECT * FROM missions WHERE slug = %s",
                (slug,),
            )
            if not mission:
                return None
    payload = _load_mission_by_id(mission["id"])
    if payload:
        cache_set(
            f"mission:{slug}",
            payload,
            current_app.config.get("REDIS_TTL_MISSION", 600),
        )
    return payload


def list_missions() -> List[Mission]:
    return sorted(load_missions().values(), key=lambda item: item.get("name", ""))


def _load_mission_by_id(mission_id: int) -> Optional[Mission]:
    with get_connection() as connection:
        if connection is None:
            return None
        with connection.cursor() as cursor:
            mission = _fetchone(
                cursor,
                "SELECT * FROM missions WHERE id = %s",
                (mission_id,),
            )
            if not mission:
                return None

            about = _fetchone(
                cursor,
                "SELECT * FROM mission_about WHERE mission_id = %s",
                (mission_id,),
            )
            values = _fetchall(
                cursor,
                "SELECT value FROM mission_values WHERE mission_id = %s",
                (mission_id,),
            )
            help_items = _fetchall(
                cursor,
                "SELECT title, description FROM mission_help WHERE mission_id = %s",
                (mission_id,),
            )
            contact = _fetchone(
                cursor,
                "SELECT * FROM mission_contact WHERE mission_id = %s",
                (mission_id,),
            )
            social = _fetchone(
                cursor,
                "SELECT * FROM mission_contact_social WHERE mission_id = %s",
                (mission_id,),
            )
            projects = _fetchall(
                cursor,
                """
                SELECT project_key, title, description, status, meeting_link, budget, closed_at
                FROM mission_projects
                WHERE mission_id = %s
                """,
                (mission_id,),
            )
            tasks = _fetchall(
                cursor,
                """
                SELECT project_key, title, status, assignee, weight
                FROM project_tasks
                WHERE mission_id = %s
                """,
                (mission_id,),
            )
            users = _fetchall(
                cursor,
                """
                SELECT name, email, institutional_email, role, status
                FROM mission_users
                WHERE mission_id = %s
                """,
                (mission_id,),
            )
            chat_messages = _fetchall(
                cursor,
                """
                SELECT from_email, from_name, to_email, message, sent_at
                FROM chat_messages
                WHERE mission_id = %s
                """,
                (mission_id,),
            )
            finance_entries = _fetchall(
                cursor,
                """
                SELECT date, type, amount, description, category, receipt_link,
                       project_key, created_by, created_at
                FROM finance_entries
                WHERE mission_id = %s
                """,
                (mission_id,),
            )
            finance_reports = _fetchall(
                cursor,
                """
                SELECT report_json, created_by, created_at
                FROM finance_reports
                WHERE mission_id = %s
                """,
                (mission_id,),
            )

    tasks_by_project = {}
    for task in tasks:
        project_key = task.get("project_key")
        tasks_by_project.setdefault(project_key, []).append(
            {
                "title": task.get("title", ""),
                "status": task.get("status", ""),
                "assignee": task.get("assignee", ""),
                "weight": task.get("weight", 1),
            }
        )

    projects_payload = []
    for project in projects:
        project_key = project.get("project_key")
        projects_payload.append(
            {
                "id": project_key,
                "title": project.get("title", ""),
                "description": project.get("description", ""),
                "status": project.get("status", ""),
                "meeting_link": project.get("meeting_link", ""),
                "budget": float(project.get("budget") or 0),
                "closed_at": project.get("closed_at") or "",
                "tasks": tasks_by_project.get(project_key, []),
            }
        )

    finance_entries_payload = []
    for entry in finance_entries:
        date_value = entry.get("date")
        if isinstance(date_value, datetime):
            date_value = date_value.strftime("%Y-%m-%d")
        finance_entries_payload.append(
            {
                "date": str(date_value or ""),
                "type": entry.get("type", ""),
                "amount": float(entry.get("amount") or 0),
                "description": entry.get("description", ""),
                "category": entry.get("category", ""),
                "receipt_link": entry.get("receipt_link", ""),
                "project_id": entry.get("project_key", ""),
                "created_by": entry.get("created_by", ""),
                "created_at": entry.get("created_at", ""),
            }
        )

    reports_payload = []
    for report in finance_reports:
        raw = report.get("report_json", "")
        try:
            report_json = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            report_json = {}
        report_json["created_by"] = report.get("created_by", "")
        report_json["created_at"] = report.get("created_at", "")
        reports_payload.append(report_json)

    about_payload = {}
    if about:
        about_payload = {
            "summary": about.get("summary", ""),
            "mission": about.get("mission", ""),
            "vision": about.get("vision", ""),
            "values": [item.get("value", "") for item in values],
            "team": about.get("team", ""),
        }

    contact_payload = {}
    if contact:
        contact_payload = {
            "email": contact.get("email", ""),
            "phone": contact.get("phone", ""),
            "address": contact.get("address", ""),
            "hours": contact.get("hours", ""),
            "social": {
                "instagram": (social or {}).get("instagram", ""),
                "facebook": (social or {}).get("facebook", ""),
                "site": (social or {}).get("site", ""),
            },
        }

    return {
        "slug": mission.get("slug", ""),
        "name": mission.get("name", ""),
        "location": mission.get("location", ""),
        "description": mission.get("description", ""),
        "verse_text": mission.get("verse_text", ""),
        "verse_ref": mission.get("verse_ref", ""),
        "meeting_link": mission.get("meeting_link", ""),
        "about": about_payload,
        "projects": projects_payload,
        "help": [
            {"title": item.get("title", ""), "description": item.get("description", "")}
            for item in help_items
        ],
        "contact": contact_payload,
        "users": users,
        "chat_messages": chat_messages,
        "finance_entries": finance_entries_payload,
        "finance_reports": reports_payload,
    }


def update_mission_meeting_link(slug: str, meeting_link: str) -> bool:
    with get_connection() as connection:
        if connection is None:
            return False
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE missions SET meeting_link = %s WHERE slug = %s",
                (meeting_link, slug),
            )
            if cursor.rowcount > 0:
                cache_delete(f"mission:{slug}", "missions:list")
                return True
            return False


def update_project_meeting_link(slug: str, project_id: str, meeting_link: str) -> bool:
    with get_connection() as connection:
        if connection is None:
            return False
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE mission_projects
                SET meeting_link = %s
                WHERE project_key = %s AND mission_id = (
                  SELECT id FROM missions WHERE slug = %s
                )
                """,
                (meeting_link, project_id, slug),
            )
            if cursor.rowcount > 0:
                cache_delete(f"mission:{slug}", "missions:list")
                return True
            return False


def add_finance_entry(slug: str, entry: Dict[str, object]) -> bool:
    with get_connection() as connection:
        if connection is None:
            return False
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO finance_entries
                (mission_id, date, type, amount, description, category, receipt_link,
                 project_key, created_by, created_at)
                VALUES (
                  (SELECT id FROM missions WHERE slug = %s),
                  %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    slug,
                    entry.get("date"),
                    entry.get("type"),
                    entry.get("amount"),
                    entry.get("description"),
                    entry.get("category"),
                    entry.get("receipt_link"),
                    entry.get("project_id"),
                    entry.get("created_by"),
                    entry.get("created_at"),
                ),
            )
            if cursor.rowcount > 0:
                cache_delete(f"mission:{slug}", "missions:list")
                return True
            return False


def update_project_budget(slug: str, project_id: str, budget: float) -> bool:
    with get_connection() as connection:
        if connection is None:
            return False
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE mission_projects
                SET budget = %s
                WHERE project_key = %s AND mission_id = (
                  SELECT id FROM missions WHERE slug = %s
                )
                """,
                (budget, project_id, slug),
            )
            if cursor.rowcount > 0:
                cache_delete(f"mission:{slug}", "missions:list")
                return True
            return False


def add_finance_report(slug: str, report: Dict[str, object]) -> bool:
    with get_connection() as connection:
        if connection is None:
            return False
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO finance_reports
                (mission_id, report_json, created_by, created_at)
                VALUES (
                  (SELECT id FROM missions WHERE slug = %s),
                  %s, %s, %s
                )
                """,
                (
                    slug,
                    json.dumps(
                        {
                            "periods": report.get("periods", {}),
                            "state": report.get("state", {}),
                        }
                    ),
                    report.get("created_by"),
                    report.get("created_at"),
                ),
            )
            if cursor.rowcount > 0:
                cache_delete(f"mission:{slug}", "missions:list")
                return True
            return False
