from typing import Dict, Iterable, List, Tuple

Task = Dict[str, object]
Project = Dict[str, object]

TASK_STATUS_DONE = "done"

STATUS_OPEN = "aberta"
STATUS_IN_PROGRESS = "em_andamento"
STATUS_PAUSED = "pausada"
STATUS_DONE = "concluida"
STATUS_CANCELED = "cancelada"


def _task_weight(task: Task) -> float:
    weight = task.get("weight", 1)
    try:
        return float(weight)
    except (TypeError, ValueError):
        return 1.0


def _task_status(task: Task) -> str:
    status = task.get("status", "")
    if isinstance(status, str):
        return status.lower()
    return ""


def tasks_progress(tasks: Iterable[Task]) -> Tuple[int, int, int]:
    total_weight = 0.0
    done_weight = 0.0
    done_count = 0
    total_count = 0

    for task in tasks:
        if not isinstance(task, dict):
            continue
        weight = _task_weight(task)
        total_weight += weight
        total_count += 1
        if _task_status(task) == TASK_STATUS_DONE:
            done_weight += weight
            done_count += 1

    if total_weight <= 0:
        return 0, done_count, total_count
    progress = int(round((done_weight / total_weight) * 100))
    return progress, done_count, total_count


def project_progress(project: Project) -> Tuple[int, int, int]:
    tasks = project.get("tasks", [])
    if isinstance(tasks, list) and tasks:
        return tasks_progress(tasks)
    return 0, 0, 0


def project_status(project: Project) -> str:
    status = project.get("status")
    if isinstance(status, str) and status:
        normalized = status.strip().lower().replace(" ", "_")
        status_map = {
            "ativo": STATUS_IN_PROGRESS,
            "em_andamento": STATUS_IN_PROGRESS,
            "em_planejamento": STATUS_OPEN,
            "planejamento": STATUS_OPEN,
            "aberta": STATUS_OPEN,
            "pausada": STATUS_PAUSED,
            "concluida": STATUS_DONE,
            "cancelada": STATUS_CANCELED,
        }
        return status_map.get(normalized, normalized)

    tasks = project.get("tasks", [])
    if not isinstance(tasks, list) or not tasks:
        return STATUS_OPEN

    statuses = {_task_status(task) for task in tasks if isinstance(task, dict)}
    if statuses and statuses.issubset({TASK_STATUS_DONE}):
        return STATUS_DONE
    if TASK_STATUS_DONE in statuses or "doing" in statuses:
        return STATUS_IN_PROGRESS
    if "blocked" in statuses:
        return STATUS_PAUSED
    return STATUS_OPEN


def mission_progress(projects: Iterable[Project]) -> int:
    progress_values: List[int] = []
    for project in projects:
        if not isinstance(project, dict):
            continue
        progress, _, _ = project_progress(project)
        progress_values.append(progress)

    if not progress_values:
        return 0
    return int(round(sum(progress_values) / len(progress_values)))


def mission_status(projects: Iterable[Project]) -> str:
    statuses = []
    for project in projects:
        if not isinstance(project, dict):
            continue
        statuses.append(project_status(project))

    if not statuses:
        return STATUS_OPEN
    if all(status == STATUS_DONE for status in statuses):
        return STATUS_DONE
    if any(status == STATUS_IN_PROGRESS for status in statuses):
        return STATUS_IN_PROGRESS
    if all(status == STATUS_PAUSED for status in statuses):
        return STATUS_PAUSED
    if any(status == STATUS_CANCELED for status in statuses):
        return STATUS_CANCELED
    return STATUS_OPEN
