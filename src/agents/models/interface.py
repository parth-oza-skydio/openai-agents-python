from __future__ import annotations
import typing

import abc
import enum
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from ..agent_output import AgentOutputSchemaBase
from ..handoffs import Handoff
from ..items import ModelResponse, TResponseInputItem, TResponseStreamEvent
from ..tool import Tool

if TYPE_CHECKING:
    from ..model_settings import ModelSettings


class ModelTracing(enum.Enum):
    DISABLED = 0
    """Tracing is disabled entirely."""

    ENABLED = 1
    """Tracing is enabled, and all data is included."""

    ENABLED_WITHOUT_DATA = 2
    """Tracing is enabled, but inputs/outputs are not included."""

    def is_disabled(self) -> bool:
        return self == ModelTracing.DISABLED

    def include_data(self) -> bool:
        return self == ModelTracing.ENABLED


class Model(abc.ABC):
    """The base interface for calling an LLM."""

    @abc.abstractmethod
    async def get_response(
        self,
        system_instructions: str | None,
        input: str | typing.List[TResponseInputItem],
        model_settings: ModelSettings,
        tools: typing.List[Tool],
        output_schema: AgentOutputSchemaBase | None,
        handoffs: typing.List[Handoff],
        tracing: ModelTracing,
        *,
        previous_response_id: str | None,
    ) -> ModelResponse:
        """Get a response from the model.

        Args:
            system_instructions: The system instructions to use.
            input: The input items to the model, in OpenAI Responses format.
            model_settings: The model settings to use.
            tools: The tools available to the model.
            output_schema: The output schema to use.
            handoffs: The handoffs available to the model.
            tracing: Tracing configuration.
            previous_response_id: the ID of the previous response. Generally not used by the model,
                except for the OpenAI Responses API.

        Returns:
            The full model response.
        """
        pass

    @abc.abstractmethod
    def stream_response(
        self,
        system_instructions: str | None,
        input: str | typing.List[TResponseInputItem],
        model_settings: ModelSettings,
        tools: typing.List[Tool],
        output_schema: AgentOutputSchemaBase | None,
        handoffs: typing.List[Handoff],
        tracing: ModelTracing,
        *,
        previous_response_id: str | None,
    ) -> typing.AsyncIterator[TResponseStreamEvent]:
        """Stream a response from the model.

        Args:
            system_instructions: The system instructions to use.
            input: The input items to the model, in OpenAI Responses format.
            model_settings: The model settings to use.
            tools: The tools available to the model.
            output_schema: The output schema to use.
            handoffs: The handoffs available to the model.
            tracing: Tracing configuration.
            previous_response_id: the ID of the previous response. Generally not used by the model,
                except for the OpenAI Responses API.

        Returns:
            An iterator of response stream events, in OpenAI Responses format.
        """
        pass


class ModelProvider(abc.ABC):
    """The base interface for a model provider.

    Model provider is responsible for looking up Models by name.
    """

    @abc.abstractmethod
    def get_model(self, model_name: str | None) -> Model:
        """Get a model by name.

        Args:
            model_name: The name of the model to get.

        Returns:
            The model.
        """
