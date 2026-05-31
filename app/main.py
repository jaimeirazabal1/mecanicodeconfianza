from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app.auth import decode_token
from app.models.user import User
from sqlalchemy import select
from app.database import async_session
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="MecaDeConfianza", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

from app.routers import auth_router, mechanic_router, review_router, tutorial_router, message_router, service_router
app.include_router(auth_router.router)
app.include_router(mechanic_router.router)
app.include_router(review_router.router)
app.include_router(tutorial_router.router)
app.include_router(message_router.router)
app.include_router(service_router.router)


async def get_user_from_token(request: Request):
    token = request.cookies.get("token")
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    async with async_session() as db:
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        if user:
            return {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role.value if user.role else None,
                "avatar_url": user.avatar_url,
            }
    return None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    user = await get_user_from_token(request)
    return templates.TemplateResponse(
        "index.html", {"request": request, "user": user}
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = await get_user_from_token(request)
    if user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "user": None}
    )


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    user = await get_user_from_token(request)
    if user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse(
        "auth/register.html", {"request": request, "user": None}
    )


@app.get("/mecanicos/{mechanic_id}", response_class=HTMLResponse)
async def mechanic_page(request: Request, mechanic_id: int):
    user = await get_user_from_token(request)
    return templates.TemplateResponse(
        "mechanics/detail.html",
        {"request": request, "user": user, "mechanic_id": mechanic_id},
    )


@app.get("/buscar", response_class=HTMLResponse)
async def search_page(request: Request):
    user = await get_user_from_token(request)
    return templates.TemplateResponse(
        "mechanics/search.html", {"request": request, "user": user}
    )


@app.get("/tutoriales", response_class=HTMLResponse)
async def tutorials_page(request: Request):
    user = await get_user_from_token(request)
    return templates.TemplateResponse(
        "tutorials/list.html", {"request": request, "user": user}
    )


@app.get("/tutoriales/{tutorial_id}", response_class=HTMLResponse)
async def tutorial_detail_page(request: Request, tutorial_id: int):
    user = await get_user_from_token(request)
    return templates.TemplateResponse(
        "tutorials/detail.html",
        {"request": request, "user": user, "tutorial_id": tutorial_id},
    )


@app.get("/perfil", response_class=HTMLResponse)
async def profile_page(request: Request):
    user = await get_user_from_token(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        "mechanics/profile.html", {"request": request, "user": user}
    )


@app.get("/mensajes", response_class=HTMLResponse)
async def messages_page(request: Request):
    user = await get_user_from_token(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        "messages/list.html", {"request": request, "user": user}
    )


@app.get("/mensajes/{other_user_id}", response_class=HTMLResponse)
async def conversation_page(request: Request, other_user_id: int):
    user = await get_user_from_token(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        "messages/conversation.html",
        {"request": request, "user": user, "other_user_id": other_user_id},
    )


@app.get("/contrataciones", response_class=HTMLResponse)
async def bookings_page(request: Request):
    user = await get_user_from_token(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        "bookings/list.html", {"request": request, "user": user}
    )


@app.get("/logout")
async def logout():
    resp = RedirectResponse(url="/")
    resp.delete_cookie("token")
    return resp
