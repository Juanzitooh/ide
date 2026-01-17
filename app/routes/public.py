from typing import Optional, Tuple

import csv
import io
from datetime import datetime, timedelta

from flask import Blueprint, current_app, redirect, render_template, request, url_for

from app.core.auth import get_current_user, require_login
from app.core.finance import (
    build_finance_entry,
    finance_periods,
    finance_state,
    parse_amount,
    sort_entries,
)
from app.core.feedback import save_feedback
from app.core.tenant import (
    add_finance_entry,
    add_finance_report,
    list_missions,
    resolve_mission,
    update_project_budget,
)
from app.core.users import find_user_by_email, get_mission_users, user_has_permission

public_bp = Blueprint("public", __name__)

MissionResponse = Tuple[Optional[dict], Optional[Tuple[str, int]]]


def _mission_or_404(slug: str) -> MissionResponse:
    mission = resolve_mission(slug)
    if mission is None:
        return None, (render_template("mission_not_found.html", slug=slug), 404)
    return mission, None


def _mission_user_from_session(mission: dict):
    current_user = get_current_user()
    if not current_user:
        return None
    email = current_user.get("email")
    if not email:
        return None
    users = get_mission_users(mission)
    return find_user_by_email(users, email)


def _parse_closed_at(value: str):
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S UTC"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


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
    can_write = user_has_permission(mission_user, "finance.write")
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
    mission_user = _mission_user_from_session(mission)
    can_view_finance = bool(mission_user and user_has_permission(mission_user, "finance.read"))
    can_write_finance = bool(mission_user and user_has_permission(mission_user, "finance.write"))
    projects = mission.get("projects", [])
    entries = mission.get("finance_entries", [])
    finance = finance_state(entries, projects) if can_view_finance else None
    cutoff = datetime.utcnow() - timedelta(days=90)
    recent_closed = []
    for project in projects:
        if not isinstance(project, dict):
            continue
        if project.get("status") != "concluida":
            continue
        closed_at = _parse_closed_at(str(project.get("closed_at", "")))
        if closed_at and closed_at >= cutoff:
            recent_closed.append(project)
    return render_template(
        "mission_dashboard.html",
        mission=mission,
        users=users,
        can_view_finance=can_view_finance,
        can_write_finance=can_write_finance,
        finance=finance,
        recent_closed=recent_closed,
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


@public_bp.route("/m/<slug>/financeiro", methods=["GET", "POST"])
def mission_finance(slug: str):
    mission, not_found = _mission_or_404(slug)
    if not_found:
        return not_found
    login_redirect = require_login(next_url=request.path)
    if login_redirect:
        return login_redirect

    mission_user = _mission_user_from_session(mission)
    if not mission_user:
        return render_template("forbidden.html", message="Acesso financeiro restrito."), 403

    role = mission_user.get("role", "")
    can_read = user_has_permission(mission_user, "finance.read") or role in {
        "lider",
        "voluntario",
    }
    if not can_read:
        return render_template("forbidden.html", message="Acesso financeiro restrito."), 403

    projects = mission.get("projects", [])
    projects_by_id = {
        project.get("id"): project
        for project in projects
        if isinstance(project, dict) and project.get("id")
    }
    if can_write:
        budget_projects = list(projects_by_id.values())
    else:
        budget_projects = []
        for project in projects_by_id.values():
            try:
                budget_value = float(project.get("budget", 0) or 0)
            except (TypeError, ValueError):
                budget_value = 0.0
            if budget_value > 0:
                budget_projects.append(project)

    entries = mission.get("finance_entries", [])
    if user_has_permission(mission_user, "finance.read"):
        entries_filtered = entries
    else:
        entries_filtered = [
            entry
            for entry in entries
            if isinstance(entry, dict)
            and entry.get("project_id")
            and entry.get("project_id") in projects_by_id
        ]

    entries_sorted = sort_entries(entries_filtered)
    state = finance_state(entries_sorted, projects_by_id.values())
    periods = finance_periods(entries_sorted)

    if request.method == "POST":
        action = request.form.get("action", "entry")

        if action == "export_csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(
                [
                    "data",
                    "tipo",
                    "valor",
                    "descricao",
                    "categoria",
                    "projeto",
                    "criado_por",
                    "criado_em",
                ]
            )
            for entry in entries_sorted:
                writer.writerow(
                    [
                        entry.get("date", ""),
                        entry.get("type", ""),
                        entry.get("amount", ""),
                        entry.get("description", ""),
                        entry.get("category", ""),
                        entry.get("project_id", ""),
                        entry.get("created_by", ""),
                        entry.get("created_at", ""),
                    ]
                )
            response = current_app.response_class(
                output.getvalue(),
                mimetype="text/csv",
            )
            response.headers["Content-Disposition"] = (
                f"attachment; filename=financeiro-{slug}.csv"
            )
            return response

        if action == "save_report":
            if not can_write:
                return render_template(
                    "forbidden.html",
                    message="Sem permissao para salvar relatorio.",
                ), 403
            report = {
                "periods": periods,
                "state": state,
                "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "created_by": mission_user.get("email", ""),
            }
            if add_finance_report(slug, report):
                return redirect(url_for("public.mission_finance", slug=slug, saved="1"))
            return render_template(
                "mission_finance.html",
                mission=mission,
                entries=entries_sorted,
                state=state,
                periods=periods,
                can_read=can_read,
                can_write=can_write,
                budget_projects=budget_projects,
                error="Nao foi possivel salvar o relatorio.",
            )

        if action == "budget":
            if not can_write:
                return render_template(
                    "forbidden.html",
                    message="Sem permissao para ajustar orcamento.",
                ), 403
            project_id = request.form.get("project_id", "").strip()
            budget_raw = request.form.get("budget", "").strip()
            budget_value = parse_amount(budget_raw)
            if not project_id or project_id not in projects_by_id:
                return render_template(
                    "mission_finance.html",
                    mission=mission,
                    entries=entries_sorted,
                    state=state,
                    periods=periods,
                    can_read=can_read,
                    can_write=can_write,
                    budget_projects=budget_projects,
                    error="Projeto invalido.",
                )
            if budget_value is None or budget_value < 0:
                return render_template(
                    "mission_finance.html",
                    mission=mission,
                    entries=entries_sorted,
                    state=state,
                    periods=periods,
                    can_read=can_read,
                    can_write=can_write,
                    budget_projects=budget_projects,
                    error="Informe um valor de orcamento valido.",
                )
            try:
                current_budget = float(projects_by_id[project_id].get("budget", 0) or 0)
            except (TypeError, ValueError):
                current_budget = 0.0
            available = state["available"] + current_budget
            if budget_value > available:
                return render_template(
                    "mission_finance.html",
                    mission=mission,
                    entries=entries_sorted,
                    state=state,
                    periods=periods,
                    can_read=can_read,
                    can_write=can_write,
                    budget_projects=budget_projects,
                    error="Orcamento acima do disponivel no caixa central.",
                )
            if update_project_budget(slug, project_id, budget_value):
                return redirect(url_for("public.mission_finance", slug=slug, saved="1"))
            return render_template(
                "mission_finance.html",
                mission=mission,
                entries=entries_sorted,
                state=state,
                periods=periods,
                can_read=can_read,
                can_write=can_write,
                budget_projects=budget_projects,
                error="Nao foi possivel atualizar o orcamento.",
            )

        if not can_write and not budget_projects:
            return render_template(
                "forbidden.html",
                message="Sem permissao de escrita.",
            ), 403
        entry, error = build_finance_entry(request.form, mission_user.get("email", ""))
        if error:
            return render_template(
                "mission_finance.html",
                mission=mission,
                entries=entries_sorted,
                state=state,
                periods=periods,
                can_read=can_read,
                can_write=can_write,
                budget_projects=budget_projects,
                error=error,
            )

        project_id = request.form.get("project_id", "").strip()
        if project_id:
            project = projects_by_id.get(project_id)
            if not project:
                return render_template(
                    "mission_finance.html",
                    mission=mission,
                    entries=entries_sorted,
                    state=state,
                    periods=periods,
                    can_read=can_read,
                    can_write=can_write,
                    budget_projects=budget_projects,
                    error="Projeto invalido.",
                )
            try:
                project_budget = float(project.get("budget", 0) or 0)
            except (TypeError, ValueError):
                project_budget = 0.0
            if project_budget <= 0:
                return render_template(
                    "mission_finance.html",
                    mission=mission,
                    entries=entries_sorted,
                    state=state,
                    periods=periods,
                    can_read=can_read,
                    can_write=can_write,
                    budget_projects=budget_projects,
                    error="Projeto sem orcamento definido.",
                )
            entry["project_id"] = project_id

        if not can_write:
            is_project_expense = (
                role in {"lider", "voluntario"}
                and entry.get("type") == "saida"
                and entry.get("project_id")
            )
            if not is_project_expense:
                return render_template(
                    "forbidden.html",
                    message="Sem permissao de escrita.",
                ), 403
        if role in {"lider", "voluntario"} and entry.get("type") == "entrada":
            return render_template(
                "forbidden.html",
                message="Somente financeiro/admin podem registrar entradas.",
            ), 403

        if entry and add_finance_entry(slug, entry):
            return redirect(url_for("public.mission_finance", slug=slug, saved="1"))
        return render_template(
            "mission_finance.html",
            mission=mission,
            entries=entries_sorted,
            state=state,
            periods=periods,
            can_read=can_read,
            can_write=can_write,
            budget_projects=budget_projects,
            error="Nao foi possivel salvar o lancamento.",
        )

    saved = request.args.get("saved") == "1"
    return render_template(
        "mission_finance.html",
        mission=mission,
        entries=entries_sorted,
        state=state,
        periods=periods,
        can_read=can_read,
        can_write=can_write,
        budget_projects=budget_projects,
        saved=saved,
    )


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
