from typing import List
from pydantic import BaseModel


class CompletionChoice(BaseModel):
    text: str
    index: int
    logprobs: float
    finish_reason: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Hello, how are you?",
                    "index": 0,
                    "logprobs": -1,
                    "finish_reason": ""
                },
            ]
        }
    }


class CompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt_tokens": 10,
                    "completion_tokens": 10,
                    "total_tokens": 20
                },
            ]
        }
    }


class CompletionResponse(BaseModel):
    id: str
    object: str = 'text_completion'
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: CompletionUsage

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123456",
                    "object": "text_completion",
                    "created": 1640995200,
                    "model": "gpt-3.5-turbo-0125",
                    "choices": [
                        {
                            "text": "Hello, how are you?",
                            "index": 0,
                            "logprobs": -1,
                            "finish_reason": ""
                        },
                    ],
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 10,
                        "total_tokens": 20
                    }
                },
            ]
        }
    }


class CompletionStreamResponse(BaseModel):
    id: str
    object: str = 'text_completion'
    created: int
    model: str
    choices: List[CompletionChoice]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123456",
                    "object": "text_completion",
                    "created": 1640995200,
                    "model": "gpt-3.5-turbo-0125",
                    "choices": [
                        {
                            "text": "Hello, how are you?",
                            "index": 0,
                            "logprobs": -1,
                            "finish_reason": ""
                        },
                    ]
                },
            ]
        }
    }
