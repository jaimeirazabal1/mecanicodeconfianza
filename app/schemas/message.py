from pydantic import BaseModel


class MessageCreate(BaseModel):
    receiver_id: int
    content: str


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    read: bool
    created_at: str | None = None
    sender_name: str | None = None

    class Config:
        from_attributes = True
