from typing import List
from pydantic import BaseModel, Field

class CompletionChoice(BaseModel):
    text: str
    index: int
    logprobs: float
    finish_reason: str


class CompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class CompletionResponse(BaseModel):
    id: str
    object: str = 'text_completion'
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: CompletionUsage


class CompletionStreamResponse(BaseModel):
    id: str
    object: str = 'text_completion'
    created: int
    model: str
    choices: List[CompletionChoice]