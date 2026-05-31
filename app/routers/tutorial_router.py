from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.mechanic import MechanicProfile
from app.models.tutorial import Tutorial
from app.schemas.tutorial import TutorialCreate, TutorialResponse
from app.auth import get_current_user

router = APIRouter(tags=["tutorials"])


@router.get("/api/tutorials")
async def list_tutorials(
    category: str = "",
    mechanic_id: int = 0,
    db=Depends(get_db),
):
    stmt = select(Tutorial).order_by(Tutorial.created_at.desc())
    if category:
        stmt = stmt.where(Tutorial.category.ilike(f"%{category}%"))
    if mechanic_id:
        stmt = stmt.where(Tutorial.mechanic_id == mechanic_id)

    result = await db.execute(stmt)
    tutorials = result.scalars().all()
    return [t.to_dict() for t in tutorials]


@router.get("/api/tutorials/{tutorial_id}")
async def get_tutorial(tutorial_id: int, db=Depends(get_db)):
    result = await db.execute(select(Tutorial).where(Tutorial.id == tutorial_id))
    tutorial = result.scalar_one_or_none()
    if not tutorial:
        raise HTTPException(status_code=404, detail="Tutorial no encontrado")
    return tutorial.to_dict()


@router.post("/api/tutorials")
async def create_tutorial(
    data: TutorialCreate,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    result = await db.execute(select(MechanicProfile).where(MechanicProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=403, detail="Solo mecánicos con perfil pueden crear tutoriales")

    tutorial = Tutorial(
        mechanic_id=profile.id,
        title=data.title,
        description=data.description,
        content=data.content,
        video_url=data.video_url,
        category=data.category,
        difficulty=data.difficulty,
    )
    db.add(tutorial)
    await db.commit()
    await db.refresh(tutorial)
    return tutorial.to_dict()


@router.delete("/api/tutorials/{tutorial_id}")
async def delete_tutorial(
    tutorial_id: int,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    result = await db.execute(select(Tutorial).where(Tutorial.id == tutorial_id))
    tutorial = result.scalar_one_or_none()
    if not tutorial:
        raise HTTPException(status_code=404, detail="Tutorial no encontrado")

    profile_result = await db.execute(select(MechanicProfile).where(MechanicProfile.user_id == user.id))
    profile = profile_result.scalar_one_or_none()
    if not profile or tutorial.mechanic_id != profile.id:
        raise HTTPException(status_code=403, detail="No puedes eliminar este tutorial")

    await db.delete(tutorial)
    await db.commit()
    return {"ok": True}
