from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from app.database import async_session
from app.models.user import User
from app.models.mechanic import MechanicProfile, Specialty, MechanicSpecialty, MechanicPhoto
from app.models.review import Review


async def search_mechanics(
    query: str = "",
    specialty: str = "",
    location: str = "",
    min_rating: float = 0,
    available_only: bool = False,
    sort_by: str = "rating",
    page: int = 1,
    per_page: int = 20,
):
    async with async_session() as db:
        stmt = select(MechanicProfile).options(
            selectinload(MechanicProfile.specialties).selectinload(MechanicSpecialty.specialty),
            selectinload(MechanicProfile.user),
        )

        conditions = []

        if available_only:
            conditions.append(MechanicProfile.available == True)

        if query:
            q = query.strip().lower()
            stmt = stmt.outerjoin(User, MechanicProfile.user_id == User.id)
            def unaccent(col):
                for a, b in [('é','e'),('É','e'),('è','e'),('È','e'),('ë','e'),('Ë','e'),
                             ('í','i'),('Í','i'),('ì','i'),('Ì','i'),('ï','i'),('Ï','i'),
                             ('ó','o'),('Ó','o'),('ò','o'),('Ò','o'),('ö','o'),('Ö','o'),
                             ('ú','u'),('Ú','u'),('ù','u'),('Ù','u'),('ü','u'),('Ü','u'),
                             ('ñ','n'),('Ñ','n'),('ç','c'),('Ç','c')]:
                    col = func.replace(col, a, b)
                return col
            name_cond = or_(
                unaccent(func.lower(MechanicProfile.business_name)).ilike(f"%{q}%"),
                unaccent(func.lower(MechanicProfile.description)).ilike(f"%{q}%"),
                unaccent(func.lower(User.name)).ilike(f"%{q}%"),
            )
            conditions.append(name_cond)

        if location:
            conditions.append(MechanicProfile.location.ilike(f"%{location}%"))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        if specialty:
            stmt = stmt.join(MechanicSpecialty).join(Specialty).where(
                Specialty.name.ilike(f"%{specialty}%")
            )

        total = await db.execute(select(func.count()).select_from(stmt.subquery()))
        total_count = total.scalar() or 0

        if sort_by == "rating":
            avg_rating_subq = (
                select(Review.mechanic_id, func.avg(Review.rating).label("avg_rating"))
                .group_by(Review.mechanic_id)
                .subquery()
            )
            stmt = stmt.outerjoin(
                avg_rating_subq,
                MechanicProfile.id == avg_rating_subq.c.mechanic_id
            ).order_by(avg_rating_subq.c.avg_rating.desc().nulls_last())
        elif sort_by == "experience":
            stmt = stmt.order_by(MechanicProfile.years_experience.desc())
        else:
            stmt = stmt.order_by(MechanicProfile.created_at.desc())

        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(stmt)
        mechanics = result.unique().scalars().all()

        return [await _enrich_mechanic(m, db) for m in mechanics], total_count


async def get_mechanic_by_id(mechanic_id: int):
    async with async_session() as db:
        result = await db.execute(
            select(MechanicProfile)
            .options(
                selectinload(MechanicProfile.specialties).selectinload(MechanicSpecialty.specialty),
                selectinload(MechanicProfile.photos),
                selectinload(MechanicProfile.user),
            )
            .where(MechanicProfile.id == mechanic_id)
        )
        mechanic = result.unique().scalar_one_or_none()
        if mechanic is None:
            return None
        return await _enrich_mechanic(mechanic, db)


async def get_mechanic_by_user_id(user_id: int):
    async with async_session() as db:
        result = await db.execute(
            select(MechanicProfile)
            .options(
                selectinload(MechanicProfile.specialties).selectinload(MechanicSpecialty.specialty),
                selectinload(MechanicProfile.photos),
                selectinload(MechanicProfile.user),
            )
            .where(MechanicProfile.user_id == user_id)
        )
        mechanic = result.unique().scalar_one_or_none()
        if mechanic is None:
            return None
        return await _enrich_mechanic(mechanic, db)


async def _enrich_mechanic(mechanic, db):
    data = mechanic.to_dict()
    data["user_name"] = mechanic.user.name if mechanic.user else None
    data["user_email"] = mechanic.user.email if mechanic.user else None
    data["user_phone"] = mechanic.user.phone if mechanic.user else None
    data["user_avatar"] = mechanic.user.avatar_url if mechanic.user else None

    rating_result = await db.execute(
        select(func.avg(Review.rating), func.count(Review.id))
        .where(Review.mechanic_id == mechanic.id)
    )
    avg_rating, review_count = rating_result.one()
    data["avg_rating"] = round(float(avg_rating), 1) if avg_rating else 0
    data["review_count"] = review_count or 0

    return data


async def get_all_specialties():
    async with async_session() as db:
        result = await db.execute(select(Specialty).order_by(Specialty.name))
        return [{"id": s.id, "name": s.name, "icon": s.icon} for s in result.scalars().all()]
