from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from app.database import get_db
from app.models.user import User
from app.models.mechanic import MechanicProfile
from app.models.service import Service, Booking, BookingStatus
from app.schemas.service import ServiceCreate, ServiceResponse, BookingCreate, BookingResponse, BookingStatusUpdate
from app.auth import get_current_user

router = APIRouter(tags=["services"])


@router.get("/api/mechanics/{mechanic_id}/services")
async def get_mechanic_services(mechanic_id: int, db=Depends(get_db)):
    result = await db.execute(
        select(Service).where(Service.mechanic_id == mechanic_id).order_by(Service.created_at.desc())
    )
    services = result.scalars().all()
    return [s.to_dict() for s in services]


@router.post("/api/services", response_model=ServiceResponse)
async def create_service(
    data: ServiceCreate,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    result = await db.execute(select(MechanicProfile).where(MechanicProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=403, detail="Solo mecánicos con perfil pueden crear servicios")

    service = Service(
        mechanic_id=profile.id,
        title=data.title,
        description=data.description,
        price=data.price,
        category=data.category,
        duration=data.duration,
    )
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return ServiceResponse(
        id=service.id,
        mechanic_id=service.mechanic_id,
        title=service.title,
        description=service.description,
        price=service.price,
        category=service.category,
        duration=service.duration,
        created_at=service.created_at.isoformat() if service.created_at else None,
        mechanic_name=profile.business_name,
    )


@router.delete("/api/services/{service_id}")
async def delete_service(
    service_id: int,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    profile_result = await db.execute(select(MechanicProfile).where(MechanicProfile.user_id == user.id))
    profile = profile_result.scalar_one_or_none()
    if not profile or service.mechanic_id != profile.id:
        raise HTTPException(status_code=403, detail="No puedes eliminar este servicio")

    await db.delete(service)
    await db.commit()
    return {"ok": True}


@router.post("/api/bookings", response_model=BookingResponse)
async def create_booking(
    data: BookingCreate,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    service_result = await db.execute(select(Service).where(Service.id == data.service_id))
    service = service_result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    if user.role.value == "mechanic":
        raise HTTPException(status_code=403, detail="Los mecánicos no pueden contratar servicios")

    booking = Booking(
        service_id=data.service_id,
        client_id=user.id,
        mechanic_id=service.mechanic_id,
        description=data.description,
        price=service.price,
        scheduled_date=data.scheduled_date,
        status=BookingStatus.PENDING,
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking.to_dict()


@router.get("/api/bookings")
async def get_bookings(
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    if user.role.value == "mechanic":
        profile_result = await db.execute(select(MechanicProfile).where(MechanicProfile.user_id == user.id))
        profile = profile_result.scalar_one_or_none()
        if not profile:
            return []
        result = await db.execute(
            select(Booking).where(Booking.mechanic_id == profile.id).order_by(Booking.created_at.desc())
        )
    else:
        result = await db.execute(
            select(Booking).where(Booking.client_id == user.id).order_by(Booking.created_at.desc())
        )
    bookings = result.scalars().all()
    return [b.to_dict() for b in bookings]


@router.put("/api/bookings/{booking_id}/status")
async def update_booking_status(
    booking_id: int,
    data: BookingStatusUpdate,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Contratación no encontrada")

    if data.status not in [s.value for s in BookingStatus]:
        raise HTTPException(status_code=400, detail="Estado inválido")

    if user.role.value == "mechanic":
        profile_result = await db.execute(select(MechanicProfile).where(MechanicProfile.user_id == user.id))
        profile = profile_result.scalar_one_or_none()
        if not profile or booking.mechanic_id != profile.id:
            raise HTTPException(status_code=403, detail="No puedes modificar esta contratación")
    elif booking.client_id != user.id:
        raise HTTPException(status_code=403, detail="No puedes modificar esta contratación")

    booking.status = BookingStatus(data.status)
    await db.commit()
    await db.refresh(booking)
    return booking.to_dict()
