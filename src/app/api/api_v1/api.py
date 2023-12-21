from fastapi import APIRouter

from app.api.api_v1.endpoints import hello, chat_bot

api_router = APIRouter()
api_router.include_router(hello.router, tags=["hello"])
api_router.include_router(chat_bot.router, prefix="/gemini", tags=["chatBot"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
# api_router.include_router(items.router, prefix="/items", tags=["items"])
