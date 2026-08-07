class AppException(Exception):
    """Base class for all expected application errors."""

    status_code: int = 500
    detail: str = "An unexpected error occurred."

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class BadRequestError(AppException):
    """400 - the request is invalid given current business rules."""

    status_code = 400
    detail = "Bad request."


class UnauthorizedError(AppException):
    """401 - missing/invalid credentials."""

    status_code = 401
    detail = "Could not validate credentials."


class ForbiddenError(AppException):
    """403 - authenticated, but not allowed to do this."""

    status_code = 403
    detail = "You do not have permission to perform this action."


class NotFoundError(AppException):
    """404 - the requested resource does not exist."""

    status_code = 404
    detail = "Resource not found."


class ConflictError(AppException):
    """409 - request conflicts with the current state (e.g. duplicate)."""

    status_code = 409
    detail = "This request conflicts with existing data."


class InternalServerError(AppException):
    """500 - something unexpected happened that isn't the client's fault."""

    status_code = 500
    detail = "Something went wrong on our end."
