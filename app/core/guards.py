from typing import Mapping, Optional

from flask import abort


def require_mission(mission: Optional[Mapping[str, str]]) -> Mapping[str, str]:
    if mission is None:
        abort(404)
    return mission
