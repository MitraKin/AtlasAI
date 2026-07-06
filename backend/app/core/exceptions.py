class CityPulseError(Exception):
    status_code: int = 500
    detail: str = "Internal server error"


class NotFoundError(CityPulseError):
    status_code = 404
    detail = "Resource not found"


class ValidationError(CityPulseError):
    status_code = 422
    detail = "Validation error"


class AgentError(CityPulseError):
    status_code = 502
    detail = "Agent processing error"


class DataUnavailableError(CityPulseError):
    status_code = 503
    detail = "Data source unavailable"
