## self correcting chain, needs memory. needs validators on the output.
## uses chat models with messages for history.
from typing import Any

from langchain.chat_models.base import BaseChatModel
from langchain.chains.llm import LLMChain
from langchain.schema import BasePromptTemplate
from langchain.callbacks.manager import Callbacks
from langwave.memory import VolatileMemory
from langchain.schema import BaseChatMessageHistory
from langchain.schema.output_parser import BaseOutputParser


## this could be modified to include non-chat models, but for now it's just chat models.
class ChatWave(LLMChain):
    """stores the history of the retries, will be forked from what is passed in"""

    history: BaseChatMessageHistory
    max_retry_attempts: int

    @classmethod
    def from_llm(
        cls,
        llm: BaseChatModel,
        history: BaseChatMessageHistory = None,
        max_retry_attempts: int = 5,
        **kwargs: Any
    ):
        return cls(llm=llm, **kwargs)
