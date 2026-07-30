from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    """
    Checks the health of a project.

    It returns 200 if the project is healthy.
    """
    return {"status": "healthy"}


@router.get("/error")
def error_check() -> None:
    """
    Checks that errors are being correctly logged.
    """
    raise Exception("This is an expected error from the error check endpoint!")
