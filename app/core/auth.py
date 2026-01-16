from typing import Dict, Optional

from flask import redirect, request, session, url_for

SessionUser = Dict[str, str]


def get_current_user() -> Optional[SessionUser]:
    user = session.get("user")
    if isinstance(user, dict):
        return user
    return None


def login_user(user: SessionUser) -> None:
    session["user"] = user


def logout_user() -> None:
    session.pop("user", None)


def require_login(next_url: Optional[str] = None):
    if get_current_user():
        return None
    if not next_url:
        next_url = request.full_path or "/"
    return redirect(url_for("auth.login", next=next_url))
