from fastapi import APIRouter, UploadFile, File, Form,Request
from fastapi.responses import HTMLResponse
from typing import Optional
from src.templates import get_chat_html
from src.router.login_router import get_user_from_session
from fastapi.responses import RedirectResponse
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get("/chat-router", response_class=HTMLResponse)
async def get_index(request: Request):
    user_email = get_user_from_session(request)
    if user_email:
        return get_chat_html()
    return RedirectResponse("/chat", status_code=303)