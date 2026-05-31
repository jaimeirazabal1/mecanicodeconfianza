from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.mechanic import MechanicProfile, MechanicPhoto, Specialty, MechanicSpecialty
from app.schemas.mechanic import MechanicProfileCreate, MechanicProfileUpdate
from app.auth import get_current_user
from app.services.mechanic_service import (
    search_mechanics, get_mechanic_by_id, get_mechanic_by_user_id,
    _enrich_mechanic, get_all_specialties,
)
import os, uuid, aiofiles

router = APIRouter(tags=["mechanics"])

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/api/mechanics")
async def list_mechanics(
    q: str = "",
    specialty: str = "",
    location: str = "",
    min_rating: float = 0,
    available: bool = False,
    sort: str = "rating",
    page: int = 1,
):
    results, total = await search_mechanics(
        query=q, specialty=specialty, location=location,
        min_rating=min_rating, available_only=available,
        sort_by=sort, page=page,
    )
    return {"mechanics": results, "total": total, "page": page}


@router.get("/api/mechanics/{mechanic_id}")
async def get_mechanic(mechanic_id: int):
    mechanic = await get_mechanic_by_id(mechanic_id)
    if not mechanic:
        raise HTTPException(status_code=404, detail="Mecánico no encontrado")
    return mechanic


@router.post("/api/mechanics/profile")
async def create_mechanic_profile(
    data: MechanicProfileCreate,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    if user.role.value != "mechanic":
        raise HTTPException(status_code=403, detail="Solo mecánicos pueden crear perfil")

    existing = await db.execute(select(MechanicProfile).where(MechanicProfile.user_id == user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ya tienes un perfil de mecánico")

    profile = MechanicProfile(
        user_id=user.id,
        business_name=data.business_name,
        description=data.description,
        years_experience=data.years_experience,
        location=data.location,
        latitude=data.latitude,
        longitude=data.longitude,
        phone_visible=data.phone_visible,
    )
    db.add(profile)
    await db.flush()

    for spec_name in data.specialties:
        spec_result = await db.execute(select(Specialty).where(Specialty.name == spec_name))
        spec = spec_result.scalar_one_or_none()
        if not spec:
            spec = Specialty(name=spec_name)
            db.add(spec)
            await db.flush()
        db.add(MechanicSpecialty(mechanic_id=profile.id, specialty_id=spec.id))

    await db.commit()
    await db.refresh(profile)
    return await _enrich_mechanic(profile, db)


@router.put("/api/mechanics/profile")
async def update_mechanic_profile(
    data: MechanicProfileUpdate,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    result = await db.execute(select(MechanicProfile).where(MechanicProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    if "specialties" in update_data:
        specs = update_data.pop("specialties")
        await db.execute(
            select(MechanicSpecialty).where(MechanicSpecialty.mechanic_id == profile.id)
        )
        existing_specs = await db.execute(
            select(MechanicSpecialty).where(MechanicSpecialty.mechanic_id == profile.id)
        )
        for es in existing_specs.scalars().all():
            await db.delete(es)
        for spec_name in specs:
            spec_result = await db.execute(select(Specialty).where(Specialty.name == spec_name))
            spec = spec_result.scalar_one_or_none()
            if not spec:
                spec = Specialty(name=spec_name)
                db.add(spec)
                await db.flush()
            db.add(MechanicSpecialty(mechanic_id=profile.id, specialty_id=spec.id))

    for key, value in update_data.items():
        setattr(profile, key, value)

    await db.commit()
    await db.refresh(profile)
    return await _enrich_mechanic(profile, db)


@router.get("/api/me/my-profile")
async def get_my_profile(user: User = Depends(get_current_user)):
    mechanic = await get_mechanic_by_user_id(user.id)
    if not mechanic:
        raise HTTPException(status_code=404, detail="No tienes perfil de mecánico")
    return mechanic


@router.post("/api/mechanics/profile/photo")
async def upload_photo(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    result = await db.execute(select(MechanicProfile).where(MechanicProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    async with aiofiles.open(filepath, "wb") as f:
        content = await file.read()
        await f.write(content)

    photo = MechanicPhoto(mechanic_id=profile.id, url=f"/static/uploads/{filename}")
    db.add(photo)
    await db.commit()
    return {"url": photo.url}


@router.get("/api/specialties")
async def list_specialties():
    return await get_all_specialties()
