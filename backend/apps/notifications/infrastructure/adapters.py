class NotificationAdapter:
    def send(self, *, recipient, subject: str, body: str, context: dict) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class NoopNotificationAdapter(NotificationAdapter):
    def send(self, *, recipient, subject: str, body: str, context: dict) -> None:
        # Intentionally no-op for open-source baseline scaffolding.
        return None


def get_adapter(channel: str) -> NotificationAdapter:
    # Channel-specific adapters can be introduced without changing application service contracts.
    return NoopNotificationAdapter()
