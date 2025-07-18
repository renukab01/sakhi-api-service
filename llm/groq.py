import os
from typing import Any

from langchain_groq import ChatGroq
from llm.base import BaseChatClient


class GroqChatClient(BaseChatClient):
    """
    This class provides a chat interface for interacting with ChatGroq.
    """
    def get_client(self, model=os.getenv("GROQ_MODEL"), **kwargs: Any) -> ChatGroq:
        """
        This method creates and returns a ChatGroq instance.

        Args:
            model (str, optional): The groq model to use. Defaults to the value of the environment variable "GROQ_MODEL".
            **kwargs: Additional arguments to be passed to the ChatGroq constructor.

        Returns:
            An instance of the ChatGroq class.
        """
        return ChatGroq(model=model, **kwargs)