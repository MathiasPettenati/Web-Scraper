from __future__ import annotations

from dataclasses import dataclass, field


class NotificationProvider:
    async def send(self, recipient: str, subject: str, body: str) -> None:
        raise NotImplementedError


@dataclass
class TestNotificationProvider(NotificationProvider):
    __test__ = False

    sent_messages: list[dict[str, str]] = field(default_factory=list)

    async def send(self, recipient: str, subject: str, body: str) -> None:
        self.sent_messages.append({"recipient": recipient, "subject": subject, "body": body})
