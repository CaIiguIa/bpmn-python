# coding=utf-8
"""
Class used for representing tGateway of BPMN 2.0 graph
"""
from enum import Enum
from typing import Literal, Optional

from pydantic import Field

from bpmn_python.graph.classes.flow_node import FlowNode, NodeType


class GatewayDirection(Enum):
    UNSPECIFIED = "Unspecified"
    CONVERGING = "Converging"
    DIVERGING = "Diverging"
    MIXED = "Mixed"

    @classmethod
    def parse(cls, value: str) -> "GatewayDirection":
        value_lower = value.lower()
        for member in cls:
            if member.name.lower() == value_lower or str(member.value).lower() == value_lower:
                return member
        raise ValueError(f"Invalid GatewayDirection value: {value}")


class Gateway(FlowNode):
    """
    Class used for representing tGateway of BPMN 2.0 graph.
    """

    gateway_direction: GatewayDirection = Field(default=GatewayDirection.UNSPECIFIED,
                                                description="Direction of the gateway")
