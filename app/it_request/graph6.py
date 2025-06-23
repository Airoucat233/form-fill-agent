import json
from typing import Literal
from langgraph.types import Command
from langgraph.graph import StateGraph, MessagesState, START, END

from .state import OverallState
from enum import Enum
import os
from typing import Any, List, Optional
from typing_extensions import Annotated

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage
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
from .prompts import (
    supervisor_instructions,
    form_fill_agent_instructions,
    supervisor_instructions1,
)

from .state import OverallState
from langgraph.prebuilt import InjectedState, create_react_agent, ToolNode
from .chat_model import qwen_max

model = qwen_max

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
) -> dict:
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
    return template


@tool
def create_request(form_data: dict) -> dict:
    """发起需求工单创建请求"""
    return {"code": 0, "messgae": "success", "data": "创建成功,工单ID:123"}


@tool
def get_ask_futher_form(form_data: FormData) -> dict:
    """获取追问表单"""
    return form_data.model_dump()


def supervisor(
    state: OverallState,
) -> Command[Literal["template_agent", "create_agent", "form_fill_agent", END]]:
    if not state.get("inited"):
        state["inited"] = True
        state["template"] = {}
        state["form_data"] = {}
        state["missing_form_data"] = {}

    llm = model.bind_tools([template_agent, create_agent, form_fill_agent])
    system_prompt = supervisor_instructions1.format()
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    response = llm.with_structured_output(SupervisorAction).invoke(messages)
    return Command(
        goto=response.next,
        update={
            **state,
            "messages": state["messages"] + [AIMessage(response.model_dump_json())],
        },
    )


def template_agent(state: OverallState) -> Command[Literal["supervisor"]]:
    """获取需求工单模版"""
    template = get_template(state=state)
    return Command(
        goto="supervisor",
        update={
            "messages": state["messages"]
            + [
                AIMessage("获取到模板如下: " + json.dumps(template, ensure_ascii=False))
            ],
            "template": template,
        },
    )


def create_agent(state: OverallState) -> Command[Literal["supervisor"]]:
    """创建需求工单"""
    response = create_request(state["form_data"])
    return Command(
        goto="supervisor",
        update={"messages": state["messages"] + [AIMessage(response)]},
    )


def form_fill_agent(state: OverallState) -> Command[Literal["supervisor"]]:
    llm = model.bind_tools([get_ask_futher_form])
    system_prompt = form_fill_agent_instructions.format(**state)
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    response = llm.with_structured_output(FormFillResult).invoke(messages)
    return Command(
        goto="supervisor",
        update={
            **state,
            "messages": state["messages"]
            + [AIMessage("模版填充结果: " + response.model_dump_json())],
        },
    )


builder = StateGraph(OverallState)
builder.add_node(supervisor)
builder.add_node(template_agent)
builder.add_node(create_agent)
builder.add_node(form_fill_agent)

builder.add_edge(START, "supervisor")
builder.add_edge("supervisor", END)

supervisor = builder.compile()

result = supervisor.stream(
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
