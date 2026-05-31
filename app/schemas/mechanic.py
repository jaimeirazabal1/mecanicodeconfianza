from pydantic import BaseModel


class MechanicProfileCreate(BaseModel):
    business_name: str | None = None
    description: str | None = None
    years_experience: int = 0
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    specialties: list[str] = []
    phone_visible: bool = True


class MechanicProfileUpdate(BaseModel):
    business_name: str | None = None
    description: str | None = None
    years_experience: int | None = None
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    available: bool | None = None
    phone_visible: bool | None = None
    specialties: list[str] | None = None


class MechanicProfileResponse(BaseModel):
    id: int
    user_id: int
    business_name: str | None = None
    description: str | None = None
    years_experience: int = 0
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    available: bool = True
    verified: bool = False
    phone_visible: bool = True
    specialties: list[str] = []
    photos: list[str] = []
    avg_rating: float = 0
    review_count: int = 0
    user_name: str | None = None
    user_email: str | None = None
    user_phone: str | None = None
    user_avatar: str | None = None

    class Config:
        from_attributes = True
