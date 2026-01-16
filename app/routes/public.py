from typing import Optional, Tuple

from flask import Blueprint, current_app, redirect, render_template, request, url_for

from app.core.auth import get_current_user, require_login
from app.core.feedback import save_feedback
from app.core.tenant import list_missions, resolve_mission
from app.core.users import find_user_by_email, get_mission_users

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


@public_bp.get("/m/<slug>/projetos/<project_id>")
def mission_project_detail(slug: str, project_id: str):
    mission, not_found = _mission_or_404(slug)
    if not_found:
        return not_found
    projects = mission.get("projects", [])
    project = next(
        (item for item in projects if item.get("id") == project_id), None
    )
    if project is None:
        return render_template("mission_not_found.html", slug=slug), 404
    tasks = project.get("tasks", [])
    return render_template(
        "mission_project_detail.html",
        mission=mission,
        project=project,
        tasks=tasks,
    )


@public_bp.get("/m/<slug>/painel")
def mission_dashboard(slug: str):
    mission, not_found = _mission_or_404(slug)
    if not_found:
        return not_found
    login_redirect = require_login(next_url=request.path)
    if login_redirect:
        return login_redirect
    users = get_mission_users(mission)
    return render_template(
        "mission_dashboard.html",
        mission=mission,
        users=users,
    )


@public_bp.get("/m/<slug>/chat")
def mission_chat(slug: str):
    mission, not_found = _mission_or_404(slug)
    if not_found:
        return not_found
    login_redirect = require_login(next_url=request.full_path)
    if login_redirect:
        return login_redirect

    current_user = get_current_user()
    users = get_mission_users(mission)
    selected_email = request.args.get("with")
    selected_user = None
    if selected_email:
        selected_user = find_user_by_email(users, selected_email)

    messages = mission.get("chat_messages", [])
    if selected_email and current_user:
        current_email = current_user.get("email")
        filtered = [
            msg
            for msg in messages
            if isinstance(msg, dict)
            and (
                (msg.get("from_email") == current_email and msg.get("to_email") == selected_email)
                or (msg.get("from_email") == selected_email and msg.get("to_email") == current_email)
            )
        ]
    else:
        filtered = []

    return render_template(
        "mission_chat.html",
        mission=mission,
        users=users,
        selected_user=selected_user,
        messages=filtered,
    )


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


@public_bp.route("/feedback", methods=["GET", "POST"])
def feedback():
    current_user = get_current_user()
    if request.method == "POST":
        feedback_type = request.form.get("type", "sugestao").strip()
        message = request.form.get("message", "").strip()
        if not message:
            return render_template(
                "feedback.html",
                error="Descreva o feedback antes de enviar.",
                submitted=False,
            )

        payload = {
            "type": feedback_type,
            "message": message,
            "email": request.form.get("email", "").strip()
            or (current_user.get("email") if current_user else ""),
            "name": request.form.get("name", "").strip()
            or (current_user.get("name") if current_user else ""),
            "page": request.form.get("page", "").strip()
            or (request.referrer or ""),
            "version": str(current_app.config.get("APP_VERSION", "")),
        }
        save_feedback(payload)
        return render_template(
            "feedback.html",
            submitted=True,
            feedback_type=feedback_type,
        )

    return render_template("feedback.html", submitted=False)
