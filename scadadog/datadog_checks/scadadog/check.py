
from typing import Any

from datadog_checks.base import AgentCheck


class ScadadogCheck(AgentCheck):
    def check(self, _):
        # type: (Any) -> None
        # Use self.instance to read the check configuration
        pass
