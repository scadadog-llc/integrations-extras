from typing import Any
from datadog_checks.base import AgentCheck


class ScadadogCheck(AgentCheck):
    def check(self, _):
        # type: (Any) -> None
        # Use self.instance to read the check configuration
        self.event(
            {
                "msg_title": "Scadadog Run ",
                "msg_text": "hello world",
                "tags": [],
            }
        )
        self.gauge('hello.world', 1, tags=['TAG_KEY:TAG_VALUE'] + self.instance.get('tags', []))
        self.service_check('scadadog.wonderware', self.OK)
