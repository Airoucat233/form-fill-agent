import json
from fastapi import FastAPI, Request, Response
from sse_starlette import EventSourceResponse
from server.api.endpoints import langgraph
from app.it_request.graph1 import assistant
import uvicorn

app = FastAPI()

app.include_router(langgraph.router, prefix="/langgraph", tags=["Langgraph"])

test_message = {
    "messages": [
        {
            "role": "user",
            "content": "我需要申请一个开发环境的账号,OA系统的管理员账号",
        }
    ],
}


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Langgraph FastAPI application!"}


@app.get("/chat")
async def chat(req: Request, response: Response):

    response.headers["Content-Type"] = "text/event-stream"
    response.headers["Cache-Control"] = "no-cache"
    initial_state = {
        "messages": [
            {
                "role": "user",
                "content": "我需要申请一个开发环境的账号,OA系统的管理员账号",
            }
        ],
        "template": {},  # 初始化模板
        "form_data": {},  # 初始化表单数据
        "missing_form_data": {},  # 初始化缺失的表单数据
        "structured_response": {},  # 初始化标志
    }

    async def event_stream():
        async for event in assistant.astream_events(
            initial_state,
            include_types=["chat_model", "tool", "visual"],
        ):
            print(event)
            print("===============")
            event_type = event["event"]
            if event_type == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield {"event": "message", "data": event["data"]["chunk"].content}
            elif event_type == "on_tool_start":
                if not event["name"].startswith("transfer_to"):
                    yield {
                        "event": "tool_start",
                        "data": {"name": event["name"]},
                    }
            elif event_type == "on_tool_end":
                if not event["name"].startswith("transfer_to"):
                    yield {
                        "event": "tool_end",
                        "data": {
                            "name": event["name"],
                            "input": event["data"]["input"],
                            "output": event["data"]["output"],
                        },
                    }
            elif event_type == "on_custom_event":
                yield {
                    "event": event["name"],
                    "data": event["data"],
                }

            # yield {"data": event["data"], "event": event["event"]}

    return EventSourceResponse(event_stream())


@app.post("/chat1")
async def chat(request: Request, response: Response):
    # 读取请求体的字符串
    user_input = await request.body()
    user_input = user_input.decode()

    response.headers["Content-Type"] = "text/event-stream"
    response.headers["Cache-Control"] = "no-cache"
    stream = assistant.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "我需要申请一个开发环境的账号,OA系统的管理员账号",
                }
            ],
        }
    )

    async def event_generator():
        # 如果是同步迭代器，用同步的for：
        for chunk in stream:
            # chunk 是当前步骤的状态字典
            # 你可以从 chunk 拿 messages 或其它你想传给前端的内容
            data = json.dumps(chunk)
            yield f"data: {data}\n\n"

    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    uvicorn.run("server.main:app", host="127.0.0.1", port=8000, reload=True)
