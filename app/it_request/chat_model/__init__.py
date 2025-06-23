from langchain_community.chat_models import ChatTongyi
from langchain_core.language_models import BaseChatModel

qwen_max = ChatTongyi(
    streaming=True,
    temperature=0.1,
    model_name="qwen-max",
    api_key="sk-4ee07326926747998474add2f2f138c9",
)

qwen_turbo = ChatTongyi(
    streaming=True,
    temperature=0.1,
    model_name="qwen-turbo",
    api_key="sk-4ee07326926747998474add2f2f138c9",
)

qwen_plus_latest = ChatTongyi(
    # streaming=True,
    temperature=0.1,
    model_name="qwen-plus-latest",
    api_key="sk-4ee07326926747998474add2f2f138c9",
)
