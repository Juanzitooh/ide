from typing import Optional, Tuple

from flask import Blueprint, render_template

from app.core.tenant import list_missions, resolve_mission

public_bp = Blueprint("public", __name__)

MissionResponse = Tuple[Optional[dict], Optional[Tuple[str, int]]]


def _mission_or_404(slug: str) -> MissionResponse:
    mission = resolve_mission(slug)
    if mission is None:
        return None, (render_template("mission_not_found.html", slug=slug), 404)
    return mission, None


@public_bp.get("/")
def index():
    mission = resolve_mission()
    if mission:
        return render_template("mission.html", mission=mission)

    missions = list_missions()
    return render_template("index.html", missions=missions)


@public_bp.get("/m/<slug>")
def mission_by_slug(slug: str):
    mission, not_found = _mission_or_404(slug)
    if not_found:
        return not_found
    return render_template("mission.html", mission=mission)


@public_bp.get("/m/<slug>/sobre")
def mission_about(slug: str):
    mission, not_found = _mission_or_404(slug)
    if not_found:
        return not_found
    about = mission.get("about", {})
    return render_template("mission_about.html", mission=mission, about=about)


@public_bp.get("/m/<slug>/projetos")
def mission_projects(slug: str):
    mission, not_found = _mission_or_404(slug)
    if not_found:
        return not_found
    projects = mission.get("projects", [])
    return render_template("mission_projects.html", mission=mission, projects=projects)


@public_bp.get("/m/<slug>/ajuda")
def mission_help(slug: str):
    mission, not_found = _mission_or_404(slug)
    if not_found:
        return not_found
    help_items = mission.get("help", [])
    return render_template("mission_help.html", mission=mission, help_items=help_items)


@public_bp.get("/m/<slug>/contato")
def mission_contact(slug: str):
    mission, not_found = _mission_or_404(slug)
    if not_found:
        return not_found
    contact = mission.get("contact", {})
    return render_template("mission_contact.html", mission=mission, contact=contact)
