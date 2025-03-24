from __future__ import annotations  # Ensures compatibility with future versions of Python

import json  # Importing json for handling JSON data
import logging  # Importing logging for logging purposes
import os  # Importing os for interacting with the operating system

from pathlib import Path  # Importing Path from pathlib for file path manipulations
from typing import Any, List, Optional, Union  # Importing type hints from typing

import backoff  # Importing backoff for retrying functions with exponential backoff
import openai  # Importing openai for interacting with OpenAI's API
import pyperclip  # Importing pyperclip for clipboard operations

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler  # Importing a callback handler for streaming stdout
from langchain.chat_models.base import BaseChatModel  # Importing the base class for chat models
from langchain.schema import (  # Importing schema-related classes and functions
    AIMessage,  # Importing AIMessage for AI-generated messages
    HumanMessage,  # Importing HumanMessage for human-generated messages
    SystemMessage,  # Importing SystemMessage for system-generated messages
    messages_from_dict,  # Importing function to convert dict to messages
    messages_to_dict,  # Importing function to convert messages to dict
)
from langchain_anthropic import ChatAnthropic  # Importing ChatAnthropic for Anthropic's chat model
from langchain_openai import AzureChatOpenAI, ChatOpenAI  # Importing Azure and OpenAI chat models

from espada.core.token_usage import TokenUsageLog  # Importing TokenUsageLog for logging token usage

# Type hint for a chat message
Message = Union[AIMessage, HumanMessage, SystemMessage]

# Set up logging
logger = logging.getLogger(__name__)


class AI:

    def __init__(
        self,
        model_name="gpt-4-turbo",
        temperature=0.1,
        azure_endpoint=None,
        streaming=True,
        vision=False,
    ):

        self.temperature = temperature
        self.azure_endpoint = azure_endpoint
        self.model_name = model_name
        self.streaming = streaming
        self.vision = (
            ("vision-preview" in model_name)
            or ("gpt-4-turbo" in model_name and "preview" not in model_name)
            or ("claude" in model_name)
        )
        self.llm = self._create_chat_model()
        self.token_usage_log = TokenUsageLog(model_name)

        logger.debug(f"Using model {self.model_name}")

    def start(self, system: str, user: Any, *, step_name: str) -> List[Message]:

        messages: List[Message] = [
            SystemMessage(content=system),
            HumanMessage(content=user),
        ]
        return self.next(messages, step_name=step_name)

    def _extract_content(self, content):

        if isinstance(content, str):
            return content
        elif isinstance(content, list) and content and "text" in content[0]:
            # Assuming the structure of list content is [{'type': 'text', 'text': 'Some text'}, ...]
            return content[0]["text"]
        else:
            return ""

    def _collapse_text_messages(self, messages: List[Message]):

        collapsed_messages = []
        if not messages:
            return collapsed_messages

        previous_message = messages[0]
        combined_content = self._extract_content(previous_message.content)

        for current_message in messages[1:]:
            if current_message.type == previous_message.type:
                combined_content += "\n\n" + self._extract_content(
                    current_message.content
                )
            else:
                collapsed_messages.append(
                    previous_message.__class__(content=combined_content)
                )
                previous_message = current_message
                combined_content = self._extract_content(current_message.content)

        collapsed_messages.append(previous_message.__class__(content=combined_content))
        return collapsed_messages

    def next(
        self,
        messages: List[Message],
        prompt: Optional[str] = None,
        *,
        step_name: str,
    ) -> List[Message]:

        if prompt:
            messages.append(HumanMessage(content=prompt))

        logger.debug(
            "Creating a new chat completion: %s",
            "\n".join([m.pretty_repr() for m in messages]),
        )

        if not self.vision:
            messages = self._collapse_text_messages(messages)

        response = self.backoff_inference(messages)

        self.token_usage_log.update_log(
            messages=messages, answer=response.content, step_name=step_name
        )
        messages.append(response)
        logger.debug(f"Chat completion finished: {messages}")

        return messages

    @backoff.on_exception(backoff.expo, openai.RateLimitError, max_tries=7, max_time=45)
    def backoff_inference(self, messages):
        """
        Perform inference using the language model while implementing an exponential backoff strategy.

        This function will retry the inference in case of a rate limit error from the OpenAI API.
        It uses an exponential backoff strategy, meaning the wait time between retries increases
        exponentially. The function will attempt to retry up to 7 times within a span of 45 seconds.

        Parameters
        ----------
        messages : List[Message]
            A list of chat messages which will be passed to the language model for processing.

        callbacks : List[Callable]
            A list of callback functions that are triggered after each inference. These functions
            can be used for logging, monitoring, or other auxiliary tasks.

        Returns
        -------
        Any
            The output from the language model after processing the provided messages.

        Raises
        ------
        openai.error.RateLimitError
            If the number of retries exceeds the maximum or if the rate limit persists beyond the
            allotted time, the function will ultimately raise a RateLimitError.

        Example
        -------
        >>> messages = [SystemMessage(content="Hello"), HumanMessage(content="How's the weather?")]
        >>> response = backoff_inference(messages)
        """
        return self.llm.invoke(messages)  # type: ignore

    @staticmethod
    def serialize_messages(messages: List[Message]) -> str:

        return json.dumps(messages_to_dict(messages))

    @staticmethod
    def deserialize_messages(jsondictstr: str) -> List[Message]:

        data = json.loads(jsondictstr)
        # Modify implicit is_chunk property to ALWAYS false
        # since Langchain's Message schema is stricter
        prevalidated_data = [
            {**item, "tools": {**item.get("tools", {}), "is_chunk": False}}
            for item in data
        ]
        return list(messages_from_dict(prevalidated_data))  # type: ignore

    def _create_chat_model(self) -> BaseChatModel:
        
        if self.azure_endpoint:
            return AzureChatOpenAI(
                azure_endpoint=self.azure_endpoint,
                openai_api_version=os.getenv(
                    "OPENAI_API_VERSION", "2024-05-01-preview"
                ),
                deployment_name=self.model_name,
                openai_api_type="azure",
                streaming=self.streaming,
                callbacks=[StreamingStdOutCallbackHandler()],
            )
        elif "claude" in self.model_name:
            return ChatAnthropic(
                model=self.model_name,
                temperature=self.temperature,
                callbacks=[StreamingStdOutCallbackHandler()],
                streaming=self.streaming,
                max_tokens_to_sample=4096,
            )
        elif self.vision:
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                streaming=self.streaming,
                callbacks=[StreamingStdOutCallbackHandler()],
                max_tokens=4096,  # vision models default to low max token limits
            )
        else:
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                streaming=self.streaming,
                callbacks=[StreamingStdOutCallbackHandler()],
            )


def serialize_messages(messages: List[Message]) -> str:
    return AI.serialize_messages(messages)


class ClipboardAI(AI):
    # Ignore not init superclass
    def __init__(self, **_):  # type: ignore
        self.vision = False
        self.token_usage_log = TokenUsageLog("clipboard_llm")

    @staticmethod
    def serialize_messages(messages: List[Message]) -> str:
        return "\n\n".join([f"{m.type}:\n{m.content}" for m in messages])

    @staticmethod
    def multiline_input():
        print("Enter/Paste your content. Ctrl-D or Ctrl-Z ( windows ) to save it.")
        content = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            content.append(line)
        return "\n".join(content)

    def next(
        self,
        messages: List[Message],
        prompt: Optional[str] = None,
        *,
        step_name: str,
    ) -> List[Message]:
        """
        Not yet fully supported
        """
        if prompt:
            messages.append(HumanMessage(content=prompt))

        logger.debug(f"Creating a new chat completion: {messages}")

        msgs = self.serialize_messages(messages)
        pyperclip.copy(msgs)
        Path("clipboard.txt").write_text(msgs)
        print(
            "Messages copied to clipboard and written to clipboard.txt,",
            len(msgs),
            "characters in total",
        )

        response = self.multiline_input()

        messages.append(AIMessage(content=response))
        logger.debug(f"Chat completion finished: {messages}")

        return messages
