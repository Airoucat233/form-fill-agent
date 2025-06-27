from typing import Dict, List, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class QueryMCPInput(BaseModel):
    """MCP查询输入"""
    field_name: str = Field(description="需要查询的字段名称")
    query: Optional[str] = Field(default=None, description="查询条件")

class CreateTicketInput(BaseModel):
    """创建工单输入"""
    form_data: Dict = Field(description="表单数据")
