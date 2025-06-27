import json
import uuid
from fastapi import FastAPI, Request, Response
from sse_starlette import EventSourceResponse
from api.endpoints import langgraph
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

# from app.it_request.graph1 import assistant
from app.it_request.graph0 import assistant
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

role_map = {"Human": "user", "AI": "assistant"}


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Langgraph FastAPI application!"}


@app.post("/chat")
async def chat(req: Request, response: Response):

    response.headers["Content-Type"] = "text/event-stream"
    response.headers["Cache-Control"] = "no-cache"
    body = await req.json()
    request = None
    if body["resume"]:
        request = Command(resume=body["resume"])
    else:
        request = {
            "messages": list(
                map(
                    lambda m: {"role": role_map[m["role"]], "content": m["content"]},
                    body["messages"],
                )
            ),
            "template": {},  # 初始化模板
            "form_fill_result": {
                "form_data": {},
                "missing_data": {},
                "ask_further": None,
            },
            "user_accept": False,
        }

    # assistant.get_state({"configurable": {"thread_id": "123456"}})

    async def event_stream():
        if not body["session_id"]:
            session_id = uuid.uuid4()
            config = {"configurable": {"thread_id": session_id}}
            yield {"event": "session_id", "data": session_id}
        else:
            config = {"configurable": {"thread_id": body["session_id"]}}
        async for event in assistant.astream_events(
            request,
            config=config,
            # include_types=["chat_model", "tool", "visual", "tool_result", "chain"],
        ):
            # print(event)
            print("===============")
            event_type = event["event"]

            result = None
            if event_type == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    result = {
                        "event": "message",
                        "data": event["data"]["chunk"].content,
                    }
                    yield result
            elif event_type == "on_tool_start":
                if not event["name"].startswith("transfer_to"):
                    result = {
                        "event": "tool_start",
                        "data": json.dumps({"name": event["name"]}, ensure_ascii=False),
                    }
                    yield result
            elif event_type == "on_tool_end":
                if not event["name"].startswith("transfer_to"):
                    result = {
                        "event": "tool_end",
                        "data": json.dumps(
                            {
                                "name": event["name"],
                                # "output": event["data"]["output"],
                            },
                            ensure_ascii=False,
                        ),
                    }
                    yield result
            elif event_type == "on_custom_event":
                result = {
                    "event": event["name"],
                    "data": json.dumps(event["data"], ensure_ascii=False),
                }
                yield result
            elif event_type == "on_chain_stream":
                interrupts = event.get("data", {}).get("chunk", {}).get("__interrupt__")
                if interrupts:
                    yield {
                        "event": "interrupt",
                        "data": json.dumps(
                            list(
                                map(
                                    lambda interrupt: {
                                        "interrupt_id": interrupt.interrupt_id,
                                        "value": interrupt.value,
                                    },
                                    interrupts,
                                )
                            ),
                            ensure_ascii=False,
                        ),
                    }
            else:
                result = event
            print(result)
            # yield (result)

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
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
