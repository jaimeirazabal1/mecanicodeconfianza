from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    mechanic_id = Column(Integer, ForeignKey("mechanic_profiles.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Float, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    mechanic = relationship("MechanicProfile", backref="reviews", lazy="joined")
    client = relationship("User", backref="reviews", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "mechanic_id": self.mechanic_id,
            "client_id": self.client_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "client_name": self.client.name if self.client else None,
            "client_avatar": self.client.avatar_url if self.client else None,
        }
