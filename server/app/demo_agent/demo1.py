import json
import os
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class GetWeatherInput(BaseModel):
    city: str = Field(description="城市名称，如'株洲市'")


# 1. 定义工具函数
@tool(args_schema=GetWeatherInput)
def get_current_weather(city: str) -> dict:
    """获取指定地点的当前天气信息。"""
    # 实际调用天气接口的逻辑
    return {"province": "湖南省", "city": "株洲市", "weather": "晴", "temperature": 20}


chat = ChatTongyi(
    model_name="qwen-max",
    temperature=0.18,
    api_key="sk-4ee07326926747998474add2f2f138c9",
)


tools = [get_current_weather]

# 4. 创建提示词模板
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个有用的助手，可以回答问题并使用工具获取信息。"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# 5. 创建工具调用代理
agent = create_tool_calling_agent(chat, tools, prompt)

# 6. 创建 AgentExecutor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# 7. 实现对话与工具调用流程 (简化)
def run_chat_completion_with_tool_calling(user_question: str):
    print(f"\n--- 用户提问: {user_question} ---")
    response = agent_executor.invoke({"input": user_question, "chat_history": []})
    print(f"--- 模型最终响应 ---")
    print(response["output"])
    return response["output"]


# 8. 运行示例
def main():
    run_chat_completion_with_tool_calling("株洲今天天气怎么样？")
    run_chat_completion_with_tool_calling("你好，你是谁？")  # 一个不需要工具调用的问题


if __name__ == "__main__":
    main()
