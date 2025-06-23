from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig

class Configuration(BaseModel):
    """系统配置"""
    model: str = Field(default="gpt-3.5-turbo", description="使用的模型名称")
    temperature: float = Field(default=0.7, description="模型温度参数")
    system_prompt: str = Field(
        default="""你是一个专业的IT需求分析助手。你的任务是：
1. 分析用户的IT需求
2. 提取关键信息
3. 填写需求工单表单
4. 必要时向用户询问更多信息

当前时间: {system_time}

请按照以下步骤工作：
1. 仔细分析用户的需求
2. 提取关键信息并填充表单
3. 如果信息不足，向用户询问
4. 确保所有必填字段都已填写
5. 生成最终的工单数据

记住：
- 保持专业和友好的态度
- 确保信息的准确性和完整性
- 必要时使用工具查询枚举值
- 清晰地向用户解释你的行动""",
        description="系统提示词模板"
    )

    @classmethod
    def from_context(cls, config: Optional[RunnableConfig] = None) -> "Configuration":
        """从上下文中获取配置"""
        return cls() 