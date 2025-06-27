from typing import List
from typing_extensions import Annotated, TypedDict
from langgraph.graph import add_messages
import operator


class OverallState(TypedDict):
    messages: Annotated[list, add_messages]
    action_loop_count: int
    template: dict
    form_data: dict
    missing_form_data: dict
    next: str
    tool_call_id: str
    inited: bool


class FormFillState(TypedDict):
    template: dict
    form_data: dict
    missing_form_data: dict
    tool_call_id: str
