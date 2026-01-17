from datetime import datetime
from typing import Dict, Iterable, List, Mapping, Optional, Tuple

FinanceEntry = Dict[str, object]

ENTRY_TYPE_IN = "entrada"
ENTRY_TYPE_OUT = "saida"
ALLOWED_TYPES = {ENTRY_TYPE_IN, ENTRY_TYPE_OUT}


def parse_amount(raw_value: str) -> Optional[float]:
    normalized = raw_value.replace(".", "").replace(",", ".")
    try:
        return float(normalized)
    except ValueError:
        return None


def build_finance_entry(
    form_data: Mapping[str, str], created_by: str
) -> Tuple[Optional[FinanceEntry], Optional[str]]:
    entry_type = form_data.get("type", "").strip().lower()
    if entry_type not in ALLOWED_TYPES:
        return None, "Tipo invalido."

    amount = parse_amount(form_data.get("amount", "").strip())
    if amount is None or amount <= 0:
        return None, "Informe um valor valido."

    date_value = form_data.get("date", "").strip()
    if not date_value:
        return None, "Informe a data."

    description = form_data.get("description", "").strip()
    if not description:
        return None, "Descreva o lancamento."

    category = form_data.get("category", "").strip()
    receipt_link = form_data.get("receipt_link", "").strip()

    entry = {
        "date": date_value,
        "type": entry_type,
        "amount": amount,
        "description": description,
        "category": category,
        "receipt_link": receipt_link,
        "created_by": created_by,
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    return entry, None


def finance_summary(entries: Iterable[FinanceEntry]) -> Dict[str, float]:
    total_in = 0.0
    total_out = 0.0
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        amount = entry.get("amount", 0)
        try:
            amount_value = float(amount)
        except (TypeError, ValueError):
            continue
        if entry.get("type") == ENTRY_TYPE_IN:
            total_in += amount_value
        elif entry.get("type") == ENTRY_TYPE_OUT:
            total_out += amount_value

    return {
        "total_in": total_in,
        "total_out": total_out,
        "balance": total_in - total_out,
    }


def sort_entries(entries: Iterable[FinanceEntry]) -> List[FinanceEntry]:
    def sort_key(item: FinanceEntry) -> Tuple[str, str]:
        date_value = str(item.get("date", ""))
        created_at = str(item.get("created_at", ""))
        return date_value, created_at

    return sorted(
        [entry for entry in entries if isinstance(entry, dict)],
        key=sort_key,
        reverse=True,
    )


def finance_state(
    entries: Iterable[FinanceEntry], projects: Iterable[Dict[str, object]]
) -> Dict[str, object]:
    central_entries = [
        entry
        for entry in entries
        if isinstance(entry, dict) and not entry.get("project_id")
    ]
    central_summary = finance_summary(central_entries)

    project_map = {}
    total_budget = 0.0
    for project in projects:
        if not isinstance(project, dict):
            continue
        project_id = project.get("id")
        if not project_id:
            continue
        budget = project.get("budget", 0)
        try:
            budget_value = float(budget)
        except (TypeError, ValueError):
            budget_value = 0.0
        total_budget += budget_value
        project_map[project_id] = {
            "id": project_id,
            "title": project.get("title", project_id),
            "budget": budget_value,
            "spent": 0.0,
            "status": project.get("status", ""),
            "closed_at": project.get("closed_at", ""),
        }

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        project_id = entry.get("project_id")
        if not project_id or project_id not in project_map:
            continue
        try:
            amount_value = float(entry.get("amount", 0))
        except (TypeError, ValueError):
            continue
        if entry.get("type") == ENTRY_TYPE_OUT:
            project_map[project_id]["spent"] += amount_value

    projects_state = []
    for project in project_map.values():
        remaining = project["budget"] - project["spent"]
        project["remaining"] = remaining
        projects_state.append(project)

    available = central_summary["balance"] - total_budget

    return {
        "central": central_summary,
        "total_budget": total_budget,
        "available": available,
        "projects": sorted(projects_state, key=lambda item: item["title"]),
    }


def _parse_entry_date(value: str) -> Optional[datetime]:
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S UTC"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def finance_periods(entries: Iterable[FinanceEntry]) -> Dict[str, Dict[str, float]]:
    now = datetime.utcnow()
    daily_key = now.strftime("%Y-%m-%d")
    weekly_key = f"{now.year}-W{now.isocalendar().week:02d}"
    monthly_key = now.strftime("%Y-%m")
    yearly_key = str(now.year)

    periods = {
        "daily": {"key": daily_key, "total_in": 0.0, "total_out": 0.0},
        "weekly": {"key": weekly_key, "total_in": 0.0, "total_out": 0.0},
        "monthly": {"key": monthly_key, "total_in": 0.0, "total_out": 0.0},
        "yearly": {"key": yearly_key, "total_in": 0.0, "total_out": 0.0},
    }

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        date_str = str(entry.get("date", ""))
        parsed = _parse_entry_date(date_str)
        if not parsed:
            continue
        try:
            amount_value = float(entry.get("amount", 0))
        except (TypeError, ValueError):
            continue

        is_in = entry.get("type") == ENTRY_TYPE_IN
        if parsed.strftime("%Y-%m-%d") == daily_key:
            key = "daily"
        elif parsed.isocalendar()[:2] == now.isocalendar()[:2]:
            key = "weekly"
        elif parsed.strftime("%Y-%m") == monthly_key:
            key = "monthly"
        elif parsed.year == now.year:
            key = "yearly"
        else:
            continue

        if is_in:
            periods[key]["total_in"] += amount_value
        else:
            periods[key]["total_out"] += amount_value

    for data in periods.values():
        data["balance"] = data["total_in"] - data["total_out"]

    return periods
