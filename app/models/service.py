from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, func, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    mechanic_id = Column(Integer, ForeignKey("mechanic_profiles.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, default=0)
    category = Column(String(100))
    duration = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    mechanic = relationship("MechanicProfile", backref="services", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "mechanic_id": self.mechanic_id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "duration": self.duration,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "mechanic_name": self.mechanic.business_name if self.mechanic else None,
        }


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mechanic_id = Column(Integer, ForeignKey("mechanic_profiles.id"), nullable=False)
    description = Column(Text)
    price = Column(Float, default=0)
    status = Column(SAEnum(BookingStatus), default=BookingStatus.PENDING)
    scheduled_date = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    service = relationship("Service", backref="bookings", lazy="joined")
    client = relationship("User", foreign_keys=[client_id], lazy="joined")
    mechanic = relationship("MechanicProfile", backref="bookings", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "service_id": self.service_id,
            "client_id": self.client_id,
            "mechanic_id": self.mechanic_id,
            "description": self.description,
            "price": self.price,
            "status": self.status.value if self.status else None,
            "scheduled_date": self.scheduled_date,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "service_title": self.service.title if self.service else None,
            "client_name": self.client.name if self.client else None,
            "mechanic_name": self.mechanic.business_name if self.mechanic else None,
        }
