import json
import os
import secrets
import urllib.parse
import urllib.request
from typing import Dict, Optional

from flask import Blueprint, abort, redirect, render_template, request, session, url_for

from app.core.auth import get_current_user, login_user, logout_user, require_login
from app.core.tenant import update_mission_meeting_link, update_project_meeting_link

auth_bp = Blueprint("auth", __name__)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
GOOGLE_MEET_CREATE_URL = "https://meet.googleapis.com/v2/spaces"
MEET_SCOPE = "https://www.googleapis.com/auth/meetings.space.created"


def _oauth_config() -> Dict[str, str]:
    return {
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", ""),
    }


def _oauth_ready() -> bool:
    cfg = _oauth_config()
    return all(cfg.values())


def _post_form(url: str, payload: Dict[str, str]) -> Dict[str, object]:
    data = urllib.parse.urlencode(payload).encode("utf-8")
    request_obj = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    with urllib.request.urlopen(request_obj, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_json(url: str, query: Dict[str, str]) -> Dict[str, object]:
    full_url = f"{url}?{urllib.parse.urlencode(query)}"
    with urllib.request.urlopen(full_url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _post_json(url: str, payload: Dict[str, object], access_token: str) -> Dict[str, object]:
    data = json.dumps(payload).encode("utf-8")
    request_obj = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request_obj, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _tokeninfo(id_token: str) -> Dict[str, object]:
    return _get_json(GOOGLE_TOKENINFO_URL, {"id_token": id_token})


def _safe_next_url(next_url: Optional[str]) -> str:
    if not next_url or not next_url.startswith("/"):
        return url_for("public.index")
    return next_url


def _build_auth_url(scopes: str, state: str, nonce: str, extra: Optional[Dict[str, str]] = None) -> str:
    cfg = _oauth_config()
    params = {
        "client_id": cfg["client_id"],
        "redirect_uri": cfg["redirect_uri"],
        "response_type": "code",
        "scope": scopes,
        "state": state,
        "nonce": nonce,
        "prompt": "select_account",
    }
    if extra:
        params.update(extra)
    return f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"


@auth_bp.get("/login")
def login():
    next_url = request.args.get("next")
    if next_url:
        session["login_next"] = next_url
    return render_template("login.html", oauth_ready=_oauth_ready())


@auth_bp.get("/logout")
def logout():
    logout_user()
    return redirect(url_for("public.index"))


@auth_bp.get("/auth/google")
def google_login():
    if not _oauth_ready():
        abort(503)

    state = secrets.token_urlsafe(16)
    nonce = secrets.token_urlsafe(16)
    session["oauth_state"] = state
    session["oauth_nonce"] = nonce

    return redirect(_build_auth_url("openid email profile", state, nonce))


@auth_bp.get("/auth/google/callback")
def google_callback():
    if not _oauth_ready():
        abort(503)

    if request.args.get("state") != session.get("oauth_state"):
        abort(400)

    code = request.args.get("code")
    if not code:
        abort(400)

    cfg = _oauth_config()
    token_payload = {
        "code": code,
        "client_id": cfg["client_id"],
        "client_secret": cfg["client_secret"],
        "redirect_uri": cfg["redirect_uri"],
        "grant_type": "authorization_code",
    }
    token_response = _post_form(GOOGLE_TOKEN_URL, token_payload)
    id_token = token_response.get("id_token")
    if not isinstance(id_token, str):
        abort(400)

    token_info = _tokeninfo(id_token)
    if token_info.get("aud") != cfg["client_id"]:
        abort(400)
    if token_info.get("nonce") != session.get("oauth_nonce"):
        abort(400)
    if token_info.get("email_verified") != "true":
        abort(400)

    email = token_info.get("email", "")
    name = token_info.get("name", "") or email.split("@")[0]
    if not email:
        abort(400)

    session.pop("oauth_state", None)
    session.pop("oauth_nonce", None)
    login_user({"email": email, "name": name})
    next_url = session.pop("login_next", None)
    return redirect(_safe_next_url(next_url))


@auth_bp.get("/auth/google/meet")
def google_meet():
    if not _oauth_ready():
        abort(503)

    login_redirect = require_login(next_url=request.full_path)
    if login_redirect:
        return login_redirect

    slug = request.args.get("slug")
    project_id = request.args.get("project_id")
    if not slug:
        abort(400)

    state = secrets.token_urlsafe(16)
    nonce = secrets.token_urlsafe(16)
    session["meet_oauth_state"] = state
    session["meet_oauth_nonce"] = nonce
    session["meet_target"] = {"slug": slug, "project_id": project_id}

    scopes = f"openid email profile {MEET_SCOPE}"
    return redirect(
        _build_auth_url(
            scopes,
            state,
            nonce,
            {"redirect_uri": url_for("auth.google_meet_callback", _external=True)},
        )
    )


@auth_bp.get("/auth/google/meet/callback")
def google_meet_callback():
    if not _oauth_ready():
        abort(503)
    if request.args.get("state") != session.get("meet_oauth_state"):
        abort(400)

    code = request.args.get("code")
    if not code:
        abort(400)

    cfg = _oauth_config()
    token_payload = {
        "code": code,
        "client_id": cfg["client_id"],
        "client_secret": cfg["client_secret"],
        "redirect_uri": url_for("auth.google_meet_callback", _external=True),
        "grant_type": "authorization_code",
    }
    token_response = _post_form(GOOGLE_TOKEN_URL, token_payload)
    access_token = token_response.get("access_token")
    id_token = token_response.get("id_token")
    if not isinstance(access_token, str) or not isinstance(id_token, str):
        abort(400)

    token_info = _tokeninfo(id_token)
    if token_info.get("aud") != cfg["client_id"]:
        abort(400)
    if token_info.get("nonce") != session.get("meet_oauth_nonce"):
        abort(400)
    if token_info.get("email_verified") != "true":
        abort(400)

    current_user = get_current_user()
    email = token_info.get("email", "")
    if current_user and email and current_user.get("email") != email:
        abort(400)

    space = _post_json(GOOGLE_MEET_CREATE_URL, {}, access_token)
    meeting_link = space.get("meetingUri")
    if not meeting_link and space.get("meetingCode"):
        meeting_link = f"https://meet.google.com/{space.get('meetingCode')}"
    if not meeting_link and space.get("name"):
        meeting_link = f"https://meet.google.com/{space.get('name')}"
    if not meeting_link:
        abort(500)

    target = session.pop("meet_target", {})
    slug = target.get("slug")
    project_id = target.get("project_id")
    if not slug:
        abort(400)

    if project_id:
        updated = update_project_meeting_link(slug, project_id, meeting_link)
    else:
        updated = update_mission_meeting_link(slug, meeting_link)
    if not updated:
        abort(404)

    session.pop("meet_oauth_state", None)
    session.pop("meet_oauth_nonce", None)

    return redirect(url_for("public.mission_dashboard", slug=slug))
