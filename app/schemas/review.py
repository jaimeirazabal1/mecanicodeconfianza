from pydantic import BaseModel, field_validator


class ReviewCreate(BaseModel):
    rating: float
    comment: str | None = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError("La calificación debe ser entre 1 y 5")
        return v


class ReviewResponse(BaseModel):
    id: int
    mechanic_id: int
    client_id: int
    rating: float
    comment: str | None = None
    created_at: str | None = None
    client_name: str | None = None
    client_avatar: str | None = None

    class Config:
        from_attributes = True
