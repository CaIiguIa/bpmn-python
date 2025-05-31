# coding=utf-8
"""
Class used for representing tEventBasedGateway of BPMN 2.0 graph
"""
from enum import Enum
from typing import ClassVar

from pydantic import Field

from bpmn_python.bpmn_python_consts import Consts
from bpmn_python.graph.classes.flow_node import NodeType
from bpmn_python.graph.classes.gateways.gateway import Gateway


class EventBasedGatewayType(Enum):
    EXCLUSIVE = "Exclusive"
    PARALLEL = "Parallel"

    @classmethod
    def parse(cls, value: str) -> "EventBasedGatewayType":
        value_lower = value.lower()
        for member in cls:
            if member.name.lower() == value_lower or str(member.value).lower() == value_lower:
                return member
        raise ValueError(f"Invalid EventBasedGatewayType value: {value}")


class EventBasedGateway(Gateway):
    """
    Class used for representing tEventBasedGateway of BPMN 2.0 graph
    """
    node_type: ClassVar[NodeType] = NodeType.EVENT_BASED
    instantiate: bool = Field(default=False)
    event_gateway_type: EventBasedGatewayType = Field(
        default=EventBasedGatewayType.parse(Consts.default_event_gateway_type),
        description="Type of the event gateway, can be 'Exclusive' or 'Parallel'"
    )
