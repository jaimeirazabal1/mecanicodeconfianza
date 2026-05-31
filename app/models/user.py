from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum, func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    CLIENT = "client"
    MECHANIC = "mechanic"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(50))
    role = Column(SAEnum(UserRole), default=UserRole.CLIENT, nullable=False)
    avatar_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "phone": self.phone,
            "role": self.role.value if self.role else None,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
