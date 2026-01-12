from typing import Dict, Iterable, List, Mapping, Set

User = Dict[str, str]

ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "admin": {"*"},
    "lider": {
        "content.write",
        "content.publish",
        "operations.use",
        "supporter.promote",
    },
    "editor": {
        "content.write",
        "content.publish",
    },
    "financeiro": {
        "finance.read",
        "finance.write",
        "donors.read",
    },
    "voluntario": {
        "operations.use",
        "content.read_internal",
    },
    "apoiador": {
        "supporter.apply",
        "updates.subscribe",
    },
}

ROLE_LABELS: Dict[str, str] = {
    "admin": "Administrador",
    "lider": "Lider",
    "editor": "Editor",
    "financeiro": "Financeiro",
    "voluntario": "Voluntario",
    "apoiador": "Apoiador",
}


def get_mission_users(mission: Mapping[str, object]) -> List[User]:
    users = mission.get("users", [])
    if not isinstance(users, list):
        return []
    return [user for user in users if isinstance(user, dict)]


def role_permissions(role: str) -> Set[str]:
    return set(ROLE_PERMISSIONS.get(role, set()))


def user_has_permission(user: Mapping[str, str], permission: str) -> bool:
    permissions = role_permissions(user.get("role", ""))
    return "*" in permissions or permission in permissions


def users_with_role(users: Iterable[User], role: str) -> List[User]:
    return [user for user in users if user.get("role") == role]
