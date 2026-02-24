"""Pydantic request/response models."""

from pydantic import BaseModel, Field


class BertScoreRequest(BaseModel):
    candidates: list[str]
    references: list[str]
    lang: str = "en"
    model_type: str = "microsoft/deberta-xlarge-mnli"


class BertScoreResponse(BaseModel):
    precision: list[float]
    recall: list[float]
    f1: list[float]
    model: str


class EmbedRequest(BaseModel):
    texts: list[str]
    model: str = "all-MiniLM-L6-v2"


class EmbedResponse(BaseModel):
    embeddings: list[list[float]]
    model: str
    dimensions: int


class HealthResponse(BaseModel):
    status: str = "ok"
    device: str


class InfoResponse(BaseModel):
    device: str
    device_name: str
    vram_total_mb: int | None = None
    vram_used_mb: int | None = None
    pytorch_version: str
    cuda_version: str | None = None
    loaded_models: list[str] = Field(default_factory=list)


class QueueStatus(BaseModel):
    max_concurrent: int
    in_flight: int
    available_slots: int
    waiting_estimate: int


class JobStatus(BaseModel):
    id: str
    type: str
    started_at: str
    items: int
    model: str
    progress: float


class StatusResponse(BaseModel):
    queue: QueueStatus
    active_jobs: list[JobStatus] = Field(default_factory=list)
