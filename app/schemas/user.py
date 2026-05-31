from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    phone: str | None = None
    role: str = "client"

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in ("client", "mechanic"):
            raise ValueError("Rol debe ser 'client' o 'mechanic'")
        return v


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    phone: str | None = None
    role: str
    avatar_url: str | None = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
