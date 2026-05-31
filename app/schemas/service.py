from pydantic import BaseModel


class ServiceCreate(BaseModel):
    title: str
    description: str | None = None
    price: float = 0
    category: str | None = None
    duration: str | None = None


class ServiceResponse(BaseModel):
    id: int
    mechanic_id: int
    title: str
    description: str | None = None
    price: float
    category: str | None = None
    duration: str | None = None
    created_at: str | None = None
    mechanic_name: str | None = None

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    service_id: int
    description: str | None = None
    scheduled_date: str | None = None


class BookingStatusUpdate(BaseModel):
    status: str


class BookingResponse(BaseModel):
    id: int
    service_id: int
    client_id: int
    mechanic_id: int
    description: str | None = None
    price: float = 0
    status: str | None = None
    scheduled_date: str | None = None
    created_at: str | None = None
    service_title: str | None = None
    client_name: str | None = None
    mechanic_name: str | None = None

    class Config:
        from_attributes = True
