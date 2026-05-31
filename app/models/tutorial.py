from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Tutorial(Base):
    __tablename__ = "tutorials"

    id = Column(Integer, primary_key=True, index=True)
    mechanic_id = Column(Integer, ForeignKey("mechanic_profiles.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text)
    video_url = Column(String(500))
    category = Column(String(100))
    difficulty = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    mechanic = relationship("MechanicProfile", backref="tutorials", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "mechanic_id": self.mechanic_id,
            "title": self.title,
            "description": self.description,
            "content": self.content,
            "video_url": self.video_url,
            "category": self.category,
            "difficulty": self.difficulty,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "mechanic_name": self.mechanic.business_name if self.mechanic and self.mechanic.business_name else None,
        }
