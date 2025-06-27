from enum import Enum
import os
from pathlib import Path
from typing import Annotated, Any, List, Optional
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from typing import Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.graph import StateGraph, START, MessagesState, END
from langgraph.types import Command
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage, HumanMessage
from langgraph.graph import add_messages
from langchain_core.callbacks.manager import (
    adispatch_custom_event,
)
from langchain_core.runnables import RunnableLambda, RunnableConfig

from .utils.pretty import pretty_print_messages
from .chat_model import qwen_max, qwen_plus
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from .prompts import (
    supervisor_instructions,
    form_fill_agent_instructions,
    supervisor_instructions1,
    supervisor_instructions2,
)

load_dotenv("./app/.env")
# 👇验证（可选）
print("LangSmith project:", os.getenv("LANGSMITH_PROJECT"))

model = qwen_plus


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


class FormData(BaseModel):
    """追问表单数据结构"""

    title: str = Field(description="表单标题")
    readonly: bool = Field(description="是否只读,默认False")
    fields: List[FormField] = Field(..., description="表单字段列表")


class Template(BaseModel):
    """表单模版"""

    type: str = Field(description="表单的类型")
    fields: dict = Field(
        description='模版字段schema,如"desc": {"type": "String", "desc": "需求详细描述", "required": True}'
    )


class FormFillResult(BaseModel):
    """表单填充结果"""

    form_data: dict = Field(default={}, description="已经识别并填充的表单数据")
    ask_futher: bool = Field(default=None, description="是否需要追问用户提供更多信息")
    missing_form_data: dict = Field(default={}, mdescription="待完善/缺失的表单数据")


class OverallState(AgentState):
    template: dict = {}
    form_fill_result: FormFillResult = {}


class FormFillState(AgentState):
    template: dict = {}
    form_fill_result: FormFillResult = {}


class TemplateState(AgentState):
    template: dict = {}


@tool("获取需求工单模版")
async def get_template(
    state: Annotated[TemplateState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    config: RunnableConfig,
) -> Command:
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
    await adispatch_custom_event(
        "tool_result",
        {
            "type": "form",
            "data": template,
        },
        config=config,
    )
    return Command(
        update={
            **state,
            "template": template,
            "messages": [ToolMessage(template, tool_call_id=tool_call_id)],
        }
    )


@tool(name_or_callable="填充表单")
async def fill_form(
    form_fill_result: FormFillResult,
    *,
    state: Annotated[FormFillState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    config: RunnableConfig,
) -> Command:
    """填充表单"""
    data = form_fill_result.model_dump_json()
    await adispatch_custom_event(
        "visual",
        {
            "type": "form",
            "data": f"""```form\n{data}\n```""",
        },
        config=config,
    )
    return Command(
        update={
            **state,
            "form_fill_result": form_fill_result,
            "messages": [ToolMessage(data, tool_call_id=tool_call_id)],
        }
    )


@tool("发起需求工单创建请求")
def create_request(form_data: dict) -> dict:
    """发起需求工单创建请求"""
    return {"code": 0, "message": "success", "data": "创建成功,工单ID:123"}


template_agent = create_react_agent(
    model=model,
    tools=[get_template],
    name="template_agent",
    prompt="""
        你是一个需求工单模版助手，根据项目经理的要求提供需求工单模版
        你有以下工具可以使用:
            1. `获取需求工单模版`:通过该工具可以获取需求工单模板
        输出要求：
            - 不可编造模板,必须是通过工具获取的
    """,
    # post_model_hook=post_template_hook,
    state_schema=TemplateState,
    # response_format=Template,
)


def form_fill_agent_propmt(state: FormFillState):
    return (
        SystemMessage(
            content=form_fill_agent_instructions.format(
                template=state["template"],
                form_fill_result=state["form_fill_result"].model_dump_json(),
            )
        )
        + state["messages"]
    )


form_fill_agent = create_react_agent(
    model=model,
    tools=[fill_form],
    name="form_fill_agent",
    prompt=form_fill_agent_propmt,
    state_schema=FormFillState,
    # response_format=FormFillResult,  # 填充agent生成的结构化数据无法通过钩子设置state，应该在调用工具get_ask_futher_form去返回结构化数据，工具名字要改下，叫生成填充结果
)

create_agent = create_react_agent(
    model=model,
    tools=[create_request],
    name="create_agent",
    prompt="你是一个需求创建助手,根据用户传入的json表单发起创建需求工单请求,返回请求结果",
)


def create_handoff_tool(*, agent_name: str, description: str | None = None):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
        state: Annotated[OverallState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        tool_message = ToolMessage(
            f"Successfully transferred to {agent_name}",
            name=name,
            tool_call_id=tool_call_id,
        )
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
    agent_name="form_fill_agent",
    description="将任务分配给需求工单填报助手",
)
assign_to_create_agent = create_handoff_tool(
    agent_name="create_agent",
    description="将任务分配给需求创建助手",
)

assign_to_final_answer_agent = create_handoff_tool(
    agent_name="final_answer_agent",
    description="最终总结并生成用户可读的回复",
)

assign_to_end = create_handoff_tool(
    agent_name=END,
    description="结束流程返回回复给用户",
)

# summarization_node = SummarizationNode(
#     token_counter=count_tokens_approximately,
#     model=model,
#     max_tokens=384,
#     max_summary_tokens=128,
#     output_messages_key="llm_input_messages",
# )
supervisor_agent = create_react_agent(
    model=model,
    tools=[
        assign_to_template_agent,
        assign_to_form_agent,
        assign_to_create_agent,
        assign_to_end,
    ],
    # pre_model_hook=summarization_node,
    prompt=supervisor_instructions2,
    state_schema=OverallState,
    name="supervisor",
)

graph = (
    StateGraph(OverallState)
    .add_node(
        supervisor_agent,
        destinations=("template_agent", "form_fill_agent", "create_agent", END),
    )
    .add_node(template_agent)
    .add_node(form_fill_agent)
    .add_node(create_agent)
    .add_edge(START, "supervisor")
    .add_edge("template_agent", "supervisor")
    .add_edge("form_fill_agent", "supervisor")
    .add_edge("create_agent", "supervisor")
)

# checkpointer = InMemorySaver()
# store = InMemoryStore()
# Compile and run
assistant = graph.compile()

if __name__ == "__main__":
    # initial_state = {
    #     "messages": [
    #         {
    #             "role": "user",
    #             "content": "我需要申请一个开发环境的账号,OA系统的管理员账号",
    #         }
    #     ],
    #     "action_loop_count": 0,  # 初始化循环计数
    #     "template": {},  # 初始化模板
    #     "form_data": {},  # 初始化表单数据
    #     "missing_form_data": {},  # 初始化缺失的表单数据
    #     "next": "",  # 初始化下一步
    #     "tool_call_id": "",  # 初始化工具调用ID
    #     "inited": False,  # 初始化标志
    # }

    initial_state = {
        "messages": [
            {
                "role": "user",
                "content": "我需要申请一个开发环境的账号,OA系统的管理员账号",
            }
        ],
        "template": {},  # 初始化模板
        "form_fill_result": {
            "form_data": {},
            "missing_data": {},
            "ask_further": None,
        },  # 初始化表单数据
    }

    async def main():
        async for chunk in assistant.astream_events(
            initial_state, include_types=["tool", "chat_model", "visual"]
        ):
            print(chunk)
            print("=================")
            # pretty_print_messages(chunk)

    import asyncio

    asyncio.run(main())
