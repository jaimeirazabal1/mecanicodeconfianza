from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.mechanic import MechanicProfile
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse
from app.auth import get_current_user

router = APIRouter(tags=["reviews"])


@router.get("/api/mechanics/{mechanic_id}/reviews")
async def get_reviews(mechanic_id: int, db=Depends(get_db)):
    result = await db.execute(
        select(Review).where(Review.mechanic_id == mechanic_id).order_by(Review.created_at.desc())
    )
    reviews = result.scalars().all()
    return [r.to_dict() for r in reviews]


@router.post("/api/mechanics/{mechanic_id}/reviews", response_model=ReviewResponse)
async def create_review(
    mechanic_id: int,
    data: ReviewCreate,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    mechanic_result = await db.execute(select(MechanicProfile).where(MechanicProfile.id == mechanic_id))
    if not mechanic_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Mecánico no encontrado")

    existing = await db.execute(
        select(Review).where(
            Review.mechanic_id == mechanic_id,
            Review.client_id == user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ya calificaste a este mecánico")

    review = Review(
        mechanic_id=mechanic_id,
        client_id=user.id,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)

    return ReviewResponse(
        id=review.id,
        mechanic_id=review.mechanic_id,
        client_id=review.client_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at.isoformat() if review.created_at else None,
        client_name=user.name,
        client_avatar=user.avatar_url,
    )
