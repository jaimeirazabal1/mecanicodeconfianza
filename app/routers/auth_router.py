from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, TokenResponse
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(tags=["auth"])


@router.post("/api/auth/register", response_model=TokenResponse)
async def register(data: UserCreate, db=Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    user = User(
        email=data.email,
        password=hash_password(data.password),
        name=data.name,
        phone=data.phone,
        role=UserRole.MECHANIC if data.role == "mechanic" else UserRole.CLIENT,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user=user)


@router.post("/api/auth/login", response_model=TokenResponse)
async def login(data: UserLogin, db=Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user=user)


@router.get("/api/auth/me")
async def get_me(user: User = Depends(get_current_user)):
    return user
