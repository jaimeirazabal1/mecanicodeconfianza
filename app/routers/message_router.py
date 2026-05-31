from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from app.database import get_db
from app.models.user import User
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageResponse
from app.auth import get_current_user

router = APIRouter(tags=["messages"])


@router.get("/api/messages")
async def get_conversations(user: User = Depends(get_current_user), db=Depends(get_db)):
    subq = (
        select(Message.id)
        .where(or_(Message.sender_id == user.id, Message.receiver_id == user.id))
        .order_by(Message.created_at.desc())
        .subquery()
    )
    result = await db.execute(
        select(Message)
        .where(Message.id.in_(select(subq.c.id)))
        .order_by(Message.created_at.desc())
    )
    messages = result.scalars().all()

    conversations = {}
    for msg in messages:
        other_id = msg.receiver_id if msg.sender_id == user.id else msg.sender_id
        if other_id not in conversations:
            conversations[other_id] = msg

    return [
        {
            "other_user_id": other_id,
            "last_message": msg.to_dict(),
            "unread": sum(1 for m in messages if m.receiver_id == user.id and not m.read and m.sender_id == other_id),
        }
        for other_id, msg in conversations.items()
    ]


@router.get("/api/messages/{other_user_id}")
async def get_conversation(
    other_user_id: int,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    result = await db.execute(
        select(Message)
        .where(
            or_(
                (Message.sender_id == user.id) & (Message.receiver_id == other_user_id),
                (Message.sender_id == other_user_id) & (Message.receiver_id == user.id),
            )
        )
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()

    await db.execute(
        select(Message).where(
            Message.sender_id == other_user_id,
            Message.receiver_id == user.id,
            Message.read == False,
        )
    )
    unread = await db.execute(
        select(Message).where(
            Message.sender_id == other_user_id,
            Message.receiver_id == user.id,
            Message.read == False,
        )
    )
    for msg in unread.scalars().all():
        msg.read = True
    await db.commit()

    return [msg.to_dict() for msg in messages]


@router.post("/api/messages", response_model=MessageResponse)
async def send_message(
    data: MessageCreate,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    if data.receiver_id == user.id:
        raise HTTPException(status_code=400, detail="No puedes enviarte mensajes a ti mismo")

    receiver = await db.execute(select(User).where(User.id == data.receiver_id))
    if not receiver.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    msg = Message(
        sender_id=user.id,
        receiver_id=data.receiver_id,
        content=data.content,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    return MessageResponse(
        id=msg.id,
        sender_id=msg.sender_id,
        receiver_id=msg.receiver_id,
        content=msg.content,
        read=msg.read,
        created_at=msg.created_at.isoformat() if msg.created_at else None,
        sender_name=user.name,
    )
