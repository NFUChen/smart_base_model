from abc import abstractmethod
from enum import Enum
from typing import Generic, Iterable, TypeVar

from typing_extensions import Literal, TypedDict

from smart_base_model.messaging.behavior_subject import BehaviorSubject


class MessageDict(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str


T = TypeVar("T")


class ModelType(Enum):
    OPENAI = "openai"


class StreamChunkMessageDict(TypedDict):
    content: str
    is_final_word: bool


class LargeLanguageModelBase(Generic[T]):
    """
    Defines the base class for large language models (LLMs) in the smart_base_model package.
    The `LargeLanguageModelBase` class is an abstract base class that provides a common interface for interacting with different types of LLMs,
    Subclasses of this class must implement the abstract methods `async_ask`, `async_chat`, `ask`, and `chat`.
    The `message_subject` attribute is a `BehaviorSubject` that can be used to observe and respond to messages emitted by the LLM during its operation.
    The `MODEL_TYPE` attribute is an `Enum` that specifies the type of LLM being used
    """

    MODEL_TYPE: ModelType
    BASE_PROMPT: str = ""

    message_subject: BehaviorSubject[StreamChunkMessageDict] = BehaviorSubject[
        StreamChunkMessageDict
    ]()

    @abstractmethod
    def async_ask(self, prompt: str) -> Iterable[StreamChunkMessageDict]:
        raise NotImplementedError()

    @abstractmethod
    def async_chat(self, prompts: list[T]) -> Iterable[StreamChunkMessageDict]:
        raise NotImplementedError()

    @abstractmethod
    def ask(self, prompt: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def chat(self, prompts: list[T]) -> str:
        raise NotImplementedError()

    @abstractmethod
    def set_system_prompt(self, prompt: str) -> None:
        raise NotImplementedError

    def get_model_name(self) -> str:
        return self.__class__.__name__
