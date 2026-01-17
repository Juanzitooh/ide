import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List

from flask import current_app

from app.config import BASE_DIR
from app.core.cache import cache_delete, cache_get, cache_set
from app.core.db import get_connection
from app.core.tenant import get_mission, list_missions


def _write_report(report: Dict[str, object]) -> None:
    reports_dir = BASE_DIR / "instance"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "test_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def _record_error(errors: List[str], message: str) -> None:
    errors.append(message)


def _check_mysql(errors: List[str]) -> None:
    with get_connection() as connection:
        if connection is None:
            _record_error(errors, "MySQL nao configurado.")
            return
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()


def _check_redis(errors: List[str]) -> None:
    try:
        cache_set("test:ping", {"ok": True}, 5)
        payload = cache_get("test:ping")
        if not payload or not payload.get("ok"):
            _record_error(errors, "Redis nao respondeu corretamente.")
        cache_delete("test:ping")
    except Exception:
        _record_error(errors, "Falha ao acessar Redis.")


def _check_missions(errors: List[str]) -> None:
    missions = list_missions()
    if not missions:
        _record_error(errors, "Nenhuma missao encontrada.")
        return
    slug = current_app.config.get("TEST_MISSION_SLUG", "teste")
    mission = get_mission(slug)
    if not mission:
        _record_error(errors, f"Missao '{slug}' nao encontrada.")


def _load_test(errors: List[str]) -> float:
    slug = current_app.config.get("TEST_MISSION_SLUG", "teste")
    iterations = int(current_app.config.get("LOAD_TEST_ITERATIONS", 200))
    concurrency = int(current_app.config.get("LOAD_TEST_CONCURRENCY", 10))

    def _task():
        mission = get_mission(slug)
        if not mission:
            raise ValueError("Missao nao encontrada no load test.")

    start = time.time()
    try:
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            for _ in range(iterations):
                executor.submit(_task)
    except Exception:
        _record_error(errors, "Falha no teste de carga.")
    elapsed = time.time() - start
    return elapsed


def run_tests() -> Dict[str, object]:
    errors: List[str] = []
    _check_mysql(errors)
    _check_redis(errors)
    _check_missions(errors)
    load_time = _load_test(errors)
    report = {
        "errors": errors,
        "load_test_seconds": round(load_time, 2) if load_time else None,
    }
    _write_report(report)
    return report
