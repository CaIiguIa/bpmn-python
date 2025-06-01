# coding=utf-8
"""
Class used for representing tInclusiveGateway of BPMN 2.0 graph
"""
from typing import Optional, ClassVar

from pydantic import Field

from bpmn_python.graph.classes.flow_node import NodeType
from bpmn_python.graph.classes.gateways.gateway import Gateway


class InclusiveGateway(Gateway):
    """
    Class used for representing tInclusiveGateway of BPMN 2.0 graph
    Fields (except inherited):
    - default: ID of default flow of gateway. Must be either None (default is optional according to BPMN 2.0 XML Schema) or String.
    """
    default: Optional[str] = Field(default=None, description="ID of the default flow for the gateway")
    node_type: ClassVar[NodeType] = NodeType.INCLUSIVE
