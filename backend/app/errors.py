class DomainError(Exception):
    """Base class for domain errors mapped to clean HTTP responses."""

    status_code: int = 400
    code: str = "domain_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(DomainError):
    status_code = 404
    code = "not_found"


class InvalidTransitionError(DomainError):
    status_code = 409
    code = "invalid_transition"


class FeedbackNotAllowedError(DomainError):
    status_code = 409
    code = "feedback_not_allowed"


class GeminiConfigError(DomainError):
    status_code = 503
    code = "ai_not_configured"


class GeminiTimeoutError(DomainError):
    status_code = 504
    code = "ai_timeout"


class GeminiRateLimitError(DomainError):
    status_code = 429
    code = "ai_rate_limited"


class GeminiMalformedResponseError(DomainError):
    status_code = 502
    code = "ai_malformed_response"


class GeminiServiceError(DomainError):
    status_code = 502
    code = "ai_service_error"
