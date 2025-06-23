from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage

class InputState(BaseModel):
    """输入状态，包含用户查询和最大步数限制"""
    query: str = Field(description="用户的查询")
    max_steps: int = Field(default=5, description="最大执行步数")

class State(BaseModel):
    """对话状态，包含消息历史和当前步数"""
    messages: List[BaseMessage] = Field(default_factory=list, description="对话历史")
    current_step: int = Field(default=0, description="当前执行步数")
    max_steps: int = Field(default=5, description="最大执行步数")
    form_data: Dict = Field(default_factory=dict, description="表单数据")
    is_last_step: bool = Field(default=False, description="是否为最后一步")
    
    @property
    def should_continue(self) -> bool:
        """判断是否应该继续执行"""
        return self.current_step < self.max_steps 