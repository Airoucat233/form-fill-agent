from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from services.langgraph_service import LanggraphService
from models.common import Message
import asyncio

router = APIRouter()
langgraph_service = LanggraphService()


@router.post("/stream/")
async def stream_langgraph_response(message: Message):
    async def generate_response():
        async for chunk in langgraph_service.process_message(message.content):
            yield chunk.encode("utf-8") + b"\n"
        await asyncio.sleep(0.1)  # Simulate some processing time

    return StreamingResponse(generate_response(), media_type="text/event-stream")
