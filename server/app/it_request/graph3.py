from enum import Enum
import os
from pathlib import Path
from typing import Annotated, Any, List, Optional
from dotenv import load_dotenv
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from typing import Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.graph import StateGraph, START, MessagesState, END
from langgraph.types import Command

from .utils.pretty import pretty_print_messages
from .chat_model import qwen_max
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

load_dotenv("./app/.env")
# 👇验证（可选）
print("LangSmith project:", os.getenv("LANGSMITH_PROJECT"))

model = qwen_max


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


def getTemplate(type: str) -> dict:
    """获取模版"""
    return {
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


def getAskFutherForm(form_data: FormData) -> dict:
    """获取追问表单"""
    return form_data.model_dump()


def create(form_data: dict) -> dict:
    """创建需求工单"""
    return {"code": 0, "messgae": "success", "data": "创建成功,工单ID:123"}


template_agent = create_react_agent(
    model=model,
    tools=[getTemplate],
    name="template_agent",
    prompt="""
        你是一个需求工单模版助手，根据项目经理的要求提供需求工单模版
    """,
)

form_agent = create_react_agent(
    model=model,
    tools=[getAskFutherForm],
    name="form_agent",
    prompt="""
        你是一个需求工单填报助手,根据上下文(用户输入和工单模板等)完成表单填报,如果需要用户提供进一步信息,调用工具生成结构化输入表单供用户填写
    """,
)

create_agent = create_react_agent(
    model=model,
    tools=[create],
    name="create_agent",
    prompt="你是一个需求创建助手,根据用户传入的json表单发起创建需求工单请求,返回请求结果",
)


def create_handoff_tool(*, agent_name: str, description: str | None = None):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
        state: Annotated[MessagesState, InjectedState],
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
assign_to_template_agent = create_handoff_tool(
    agent_name="template_agent",
    description="将任务分配给需求工单模版助手",
)

assign_to_form_agent = create_handoff_tool(
    agent_name="form_agent",
    description="将任务分配给需求工单填报助手",
)
assign_to_create_agent = create_handoff_tool(
    agent_name="create_agent",
    description="将任务分配给需求创建助手",
)

# Create supervisor workflow
# graph = create_supervisor(
#     [template_agent, form_agent, create_agent],
#     model=model,
#     prompt=(
#         """
#         你是一个数字化需求工单创建项目经理,负责接收用户的数字化需求，你管理三个助手,分别是
#         1. 需求工单模版助手:负责需求模版的获取
#         2. 需求工单填报助手:负责根据模版填报表单,如果必要字段信息不足,生成待填报表单供用户完善
#         3. 需求创建助手:接收符合模版定义的表单数据发起表单创建申请,返回创建结果
#         你需要识别用户意图，创建对应模板的需求工单，分配任务给助手时，你需要给出原因
#         """
#     ),
#     output_mode="full_history",
# )
supervisor_agent = create_react_agent(
    model=model,
    tools=[assign_to_template_agent, assign_to_form_agent, assign_to_create_agent],
    prompt=(
        """
        你是一个数字化需求工单创建项目经理,负责接收用户的数字化需求，你管理三个助手,分别是
        1. 需求工单模版助手:负责需求模版的获取
        2. 需求工单填报助手:负责根据模版填报表单,如果必要字段信息不足,生成待填报表单供用户完善
        3. 需求创建助手:接收符合模版定义的表单数据发起表单创建申请,返回创建结果
        你需要识别用户意图，创建对应模板的需求工单，分配任务给助手时，你需要给出原因
        """
    ),
    name="supervisor",
)

graph = (
    StateGraph(MessagesState)
    # NOTE: `destinations` is only needed for visualization and doesn't affect runtime behavior
    .add_node(
        supervisor_agent,
        destinations=("template_agent", "form_agent", "create_agent", END),
    )
    .add_node(template_agent)
    .add_node(form_agent)
    .add_node(create_agent)
    .add_edge(START, "supervisor")
    .add_edge("template_agent", "supervisor")
    .add_edge("form_agent", "supervisor")
    .add_edge("create_agent", "supervisor")
)

checkpointer = InMemorySaver()
store = InMemoryStore()
# Compile and run
app = graph.compile(store=store)
result = app.stream(
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
