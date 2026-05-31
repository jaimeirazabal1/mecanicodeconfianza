from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.database import Base


class MechanicProfile(Base):
    __tablename__ = "mechanic_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    business_name = Column(String(255))
    description = Column(Text)
    years_experience = Column(Integer, default=0)
    location = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    available = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)
    phone_visible = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="mechanic_profile", lazy="joined")
    specialties = relationship("MechanicSpecialty", back_populates="mechanic", cascade="all, delete-orphan")
    photos = relationship("MechanicPhoto", back_populates="mechanic", cascade="all, delete-orphan")

    def to_dict(self):
        try:
            specs = [s.specialty.name for s in self.specialties] if self.specialties is not None else []
        except Exception:
            specs = []
        try:
            photos = [p.url for p in self.photos] if self.photos is not None else []
        except Exception:
            photos = []
        try:
            user_name = self.user.name if self.user else None
        except Exception:
            user_name = None
        return {
            "id": self.id,
            "user_id": self.user_id,
            "business_name": self.business_name,
            "description": self.description,
            "years_experience": self.years_experience,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "available": self.available,
            "verified": self.verified,
            "phone_visible": self.phone_visible,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "specialties": specs,
            "photos": photos,
        }


class Specialty(Base):
    __tablename__ = "specialties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    icon = Column(String(50))


class MechanicSpecialty(Base):
    __tablename__ = "mechanic_specialties"

    id = Column(Integer, primary_key=True, index=True)
    mechanic_id = Column(Integer, ForeignKey("mechanic_profiles.id"), nullable=False)
    specialty_id = Column(Integer, ForeignKey("specialties.id"), nullable=False)

    mechanic = relationship("MechanicProfile", back_populates="specialties")
    specialty = relationship("Specialty")


class MechanicPhoto(Base):
    __tablename__ = "mechanic_photos"

    id = Column(Integer, primary_key=True, index=True)
    mechanic_id = Column(Integer, ForeignKey("mechanic_profiles.id"), nullable=False)
    url = Column(String(500), nullable=False)
    caption = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    mechanic = relationship("MechanicProfile", back_populates="photos")
