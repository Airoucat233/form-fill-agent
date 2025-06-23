from enum import Enum
import os
from typing import Any, List, Optional
from typing_extensions import Annotated

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END, MessagesState
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from langgraph.types import Command

from .utils.pretty import pretty_print_messages


from .config import Configuration
from .chat_model import qwen_max, qwen_turbo
from .prompts import supervisor_instructions, form_fill_agent_instructions

from .state import OverallState
from langgraph.prebuilt import InjectedState, create_react_agent, ToolNode

# from .prompts import (

# )

load_dotenv("./app/.env")
# 👇验证（可选）
print("LangSmith project:", os.getenv("LANGSMITH_PROJECT"))


class InputType(str, Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    SELECT = "select"
    DATE = "date"


class FormField(BaseModel):
    """表单字段模型"""

    id: str = Field(..., description="字段英文名")
    label: str = Field(..., description="字段中文名")
    value: Optional[Any] = Field(None, description="字段值")
    data_type: str = Field(..., description="字段类型 java类型")
    input_type: InputType = Field(..., description="输入类型")
    required: bool = Field(False, description="是否必填")
    description: Optional[str] = Field(None, description="字段描述")
    default_value: Optional[Any] = Field(None, description="默认值")
    enum_values: Optional[List[Any]] = Field(None, description="枚举值")

    # class Config:
    #     """Pydantic 配置"""

    #     use_enum_values = True  # 使用枚举值而不是枚举对象
    #     arbitrary_types_allowed = True  # 允许任意类型


class FormData(BaseModel):
    """追问表单数据结构"""

    title: str = Field(description="表单标题")
    readonly: bool = Field(description="是否只读,默认False")
    fields: List[FormField] = Field(..., description="表单字段列表")


class FormFillResult(BaseModel):
    """表单填充结果"""

    form_data: dict = Field(description="已经识别并填充的表单数据")
    ask_futher: bool = Field(description="是否需要追问用户提供更多信息")
    missing_form_data: dict = Field(default={}, mdescription="待完善/缺失的表单数据")


class SupervisorAction(BaseModel):
    """下一步动作"""

    description: str = Field(description="描述当前状态和下一步要执行的动作")
    next: str = Field(description="下一步要执行的节点")


def get_template(
    state: OverallState,
) -> OverallState:
    """获取需求工单模版"""
    template = {
        "type": "账号开通需求",
        "fields": {
            "targetSystem": {
                "type": "String",
                "desc": "目标系统名称",
                "required": True,
            },
            "user": {"type": "String", "desc": "用户ID", "required": True},
            "role": {"type": "String", "desc": "要开通的角色", "required": True},
            "desc": {"type": "String", "desc": "需求详细描述", "required": True},
        },
    }
    state["template"] = template
    return state


@tool
def create_request(form_data: dict) -> dict:
    """发起需求工单创建请求"""
    return {"code": 0, "messgae": "success", "data": "创建成功,工单ID:123"}


@tool
def get_ask_futher_form(form_data: FormData) -> dict:
    """获取追问表单"""
    return form_data.model_dump()


form_fill_agent = create_react_agent(
    model=qwen_max,
    tools=[get_ask_futher_form],
    name="form_fill_agent",
    prompt=form_fill_agent_instructions,
    response_format=FormFillResult,
)


def create_handoff_tool(*, agent_name: str, description: str | None = None):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
        state: Annotated[OverallState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        return Command(
            goto=agent_name,
            update={**state, "messages": state["messages"] + [tool_message]},
            graph=Command.PARENT,
        )

    return handoff_tool


# Handoffs
transfor_to_form_fill_agent = create_handoff_tool(
    agent_name="form_fill_agent",
    description="将任务分配给表单填报助手",
)

supervisor_agent = create_react_agent(
    model=qwen_max,
    tools=[get_template, create_request, transfor_to_form_fill_agent],
    prompt=supervisor_instructions,
    name="supervisor",
)

builder = StateGraph(OverallState, config_schema=Configuration)
builder.add_node(
    supervisor_agent,
    destinations=("form_fill_agent", END),
)
builder.add_node(form_fill_agent)

# builder.add_node("finalize_answer", finalize_answer)

builder.add_edge(START, "supervisor")

builder.add_edge("form_fill_agent", "supervisor")

graph = builder.compile(name="it_request-agent")

result = graph.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "我需要申请一个开发环境的账号,OA系统的管理员账号",
            }
        ],
    }
)
for chunk in result:
    pretty_print_messages(chunk)
