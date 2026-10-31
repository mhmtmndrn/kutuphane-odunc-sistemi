"""Rule violations raised by services (plan §4.0)."""


class RuleViolation(Exception):
    """A business rule refused the operation; ``message`` is shown to staff."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
