# coding=utf-8
"""
Class used for representing tGateway of BPMN 2.0 graph
"""
from typing import Literal

from pydantic import Field

from bpmn_python.graph.classes.flow_node import FlowNode, NodeType


class Gateway(FlowNode):
    """
    Class used for representing tGateway of BPMN 2.0 graph.
    """

    gateway_direction: Literal["Unspecified", "Converging", "Diverging", "Mixed"] = Field(
        default="Unspecified", description="Direction of the gateway"
    )

class GatewayType(NodeType):
    EXCLUSIVE = "exclusiveGateway"
    INCLUSIVE = "inclusiveGateway"
    PARALLEL = "parallelGateway"
    EVENT_BASED = "eventBasedGateway"
    COMPLEX = "complexGateway"