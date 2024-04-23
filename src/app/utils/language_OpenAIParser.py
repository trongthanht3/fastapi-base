from typing import List, Union

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.outputs import ChatGeneration, Generation

from langchain.agents.agent import MultiActionAgentOutputParser
from langchain.agents.output_parsers.openai_tools import parse_ai_message_to_openai_tool_action


class OpenAIToolsAgentOutputParserWithLanguage(MultiActionAgentOutputParser):
    """Parses a message into agent actions/finish.

    Is meant to be used with OpenAI models, as it relies on the specific
    tool_calls parameter from OpenAI to convey what tools to use.

    If a tool_calls parameter is passed, then that is used to get
    the tool names and tool inputs.

    If one is not passed, then the AIMessage is assumed to be the final output.
    """

    @property
    def _type(self) -> str:
        return "openai-tools-agent-output-parser"

    def parse_result(
        self, result: List[Generation], *, partial: bool = False
    ) -> Union[List[AgentAction], AgentFinish]:
        if not isinstance(result[0], ChatGeneration):
            raise ValueError(
                "This output parser only works on ChatGeneration output")
        message = result[0].message
        return parse_ai_message_to_openai_tool_action(message)

    def parse(self, text: str) -> Union[List[AgentAction], AgentFinish]:
        raise ValueError("Can only parse messages")
