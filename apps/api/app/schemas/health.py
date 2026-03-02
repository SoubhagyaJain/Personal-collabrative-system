from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    model_version: str
    git_sha: str
    db: str
    redis: str
    model_loaded: bool
    artifact_version: str
