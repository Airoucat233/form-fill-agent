from enum import Enum
import os
from typing import Any, List, Optional
from typing_extensions import Annotated

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from .utils.pretty import pretty_print_messages


from .config import Configuration
from .chat_model import qwen_max, qwen_turbo
from .prompts import supervisor_instructions, form_fill_agent_instructions

from .state import FormFillState, OverallState
from langgraph.prebuilt import InjectedState

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
    state["messages"] += [ToolMessage(template, tool_call_id=state["tool_call_id"])]
    return state


@tool
def create_request(form_data: dict) -> dict:
    """发起需求工单创建请求"""
    return {"code": 0, "messgae": "success", "data": "创建成功,工单ID:123"}


@tool
def get_ask_futher_form(form_data: FormData) -> dict:
    """获取追问表单"""
    return form_data.model_dump()


def form_fill_agent(state: OverallState) -> OverallState:
    """表单填充助手，负责根据用户输入和工单模板完成表单数据的填充和验证。

    分析用户输入和工单模板，提取相关信息并填充到表单中。对于缺失的必要信息，
    生成结构化的追问表单。使用结构化输出来确保表单数据的完整性和正确性。

    参数:
        state: 当前图状态，包含：
            - messages: 用户输入消息
            - template: 工单模板数据
            - form_data: 当前表单数据
            - missing_form_data: 当前表单缺失数据

    返回:
        更新后的状态，包含：
            - form_data: 填充后的表单数据
            - validation_errors: 验证错误信息
            - metadata: 处理元数据，如处理时间、来源等

    处理流程:
        1. 分析工单模板中的字段要求
        2. 从用户输入中提取相关信息
        3. 验证必填字段的完整性
        4. 检查字段值的格式和类型
        5. 生成追问表单（如果需要）
        6. 更新状态并返回

    异常处理:
        - 模板缺失：返回错误信息
        - 必填字段缺失：生成追问表单
        - 字段格式错误：记录验证错误
    """
    llm = qwen_max.bind_tools([get_ask_futher_form])
    system_prompt = form_fill_agent_instructions.format(**state)
    messages = [SystemMessage(content=system_prompt)] + list([state["messages"][-1]])
    form_fill_result = llm.with_structured_output(FormFillResult).invoke(messages)
    state["form_data"] = form_fill_result["form_data"]
    state["missing_form_data"] = form_fill_result["missing_form_data"]
    return state


def dynamic_route(
    state: OverallState,
    config: RunnableConfig,
) -> OverallState:
    return state["next"]


def supervisor(state: OverallState, config: RunnableConfig) -> OverallState:
    config = Configuration.from_runnable_config(config)
    state["action_loop_count"] = state.get("action_loop_count", 0) + 1
    state["next"] = None
    if state["action_loop_count"] == 1:
        # 初始化
        state["form_data"] = {}
        state["missing_form_data"] = {}
        state["template"] = {}
    if state["action_loop_count"] > config.max_action_loop_count:
        print("超过最大动作数,终止")
        state["next"] = "END"
        return state
    else:
        print(f"第{state['action_loop_count']}个动作")

    llm = qwen_max.bind_tools([get_template, create_request, form_fill_agent])
    system_prompt = supervisor_instructions.format()
    # res = llm.with_structured_output(SupervisorAction).invoke(prompt)
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    res = llm.invoke(messages)
    state["messages"] += [res]
    if res.tool_calls and res.tool_calls[0]:
        state["next"] = res.tool_calls[0]["name"]
        state["tool_call_id"] = res.tool_calls[0]["id"]
    else:
        state["next"] = "END"
    return state


builder = StateGraph(OverallState, config_schema=Configuration)

builder.add_node("supervisor", supervisor)
builder.add_node("form_fill_agent", form_fill_agent)
builder.add_node("get_template", get_template)
builder.add_node("create_request", create_request)
# builder.add_node("finalize_answer", finalize_answer)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges(
    "supervisor",
    dynamic_route,
    {
        "get_template": "get_template",
        "form_fill_agent": "form_fill_agent",
        "create_request": "create_request",
        "END": END,
    },
)

builder.add_edge("get_template", "supervisor")
builder.add_edge("form_fill_agent", "supervisor")
builder.add_edge("create_request", "supervisor")

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
