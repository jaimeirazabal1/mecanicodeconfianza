from pydantic import BaseModel


class TutorialCreate(BaseModel):
    title: str
    description: str | None = None
    content: str | None = None
    video_url: str | None = None
    category: str | None = None
    difficulty: str | None = None


class TutorialResponse(BaseModel):
    id: int
    mechanic_id: int
    title: str
    description: str | None = None
    content: str | None = None
    video_url: str | None = None
    category: str | None = None
    difficulty: str | None = None
    created_at: str | None = None
    mechanic_name: str | None = None

    class Config:
        from_attributes = True
