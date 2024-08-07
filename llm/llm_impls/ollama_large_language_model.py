import pprint
from typing import Iterable, Literal
from typing_extensions import TypedDict
import partial_json_parser
import ollama
from loguru import logger

from smart_base_model.llm.large_language_model_base import (
    LargeLanguageModelBase,
    StreamChunkMessageDict,
)


class OllamaModelConfig(TypedDict):
    mode: Literal["text", "json"]
    host: str
    port: int
    model_name: Literal[
        "llama3",
        "llama3:70b",
        "phi3",
        "phi3:medium",
        "gemma:2b",
        "gemma:7b",
        "mistral",
        "moondream",
        "neural-chat",
        "starling-lm",
        "codellama",
        "llama2-uncensored",
        "llava",
        "solar",
        "llava:34b",
        "codellama:34b",
        "codellama:13b",
    ]


class OllamaModel(LargeLanguageModelBase[ollama.Message]):
    def __init__(self, model_config: OllamaModelConfig) -> None:
        self.system_prompt_dict: ollama.Message = {
            "role": "system",
            "content": "",
        }
        self.model_config = model_config
        url = f'http://{model_config["host"]}:{model_config["port"]}'

        self.model_name = model_config["model_name"]

        self.client = ollama.Client(url)
        self.mode = model_config["mode"]

    def set_system_prompt(self, prompt: str) -> None:
        self.system_prompt_dict: ollama.Message = {
            "role": "system",
            "content": prompt,
        }

    def ask(self, prompt: str) -> str:
        return self.chat([{"role": "user", "content": prompt}])

    def chat(self, prompts: list[ollama.Message]) -> str:
        messages: list[ollama.Message] = [self.system_prompt_dict, *prompts]
        response = self.client.chat(
            model=self.model_name,
            messages=messages,
            format=("json" if self.is_json_mode() else ""),
        )
        logger.info(f"[CHAT RESPONSE]\n {pprint.pformat(response)}")
        return response["message"]["content"]  # type: ignore

    def async_chat(
        self, prompts: list[ollama.Message]
    ) -> Iterable[StreamChunkMessageDict]:
        messages: list[ollama.Message] = [self.system_prompt_dict, *prompts]
        stream = self.client.chat(
            model=self.model_name,
            messages=messages,
            format=("json" if self.mode == "json" else ""),
            stream=True,
        )
        current_message = ""
        for chunk in stream:
            chunk_message = chunk["message"]["content"]  # type: ignore
            if chunk is None:
                continue
            current_message += chunk_message
            message_chunk: StreamChunkMessageDict = {
                "content":  partial_json_parser.ensure_json(current_message) if self.is_json_mode() else current_message,
                "is_final_word": False,
            }
            yield message_chunk
        message_chunk["is_final_word"] = True
        yield message_chunk

    def is_json_mode(self) -> bool:
        return self.mode == "json"    

    def async_ask(self, prompt: str) -> Iterable[StreamChunkMessageDict]:
        for chunk in self.async_chat([{"role": "user", "content": prompt}]):
            yield chunk
