# coding=utf-8
"""
Class used for representing tFlowNode of BPMN 2.0 graph
"""
from enum import Enum
from typing import List, ClassVar

from pydantic import Field

from bpmn_python.graph.classes.flow_element import FlowElement


class NodeType(Enum):
    BASE = ""

#   Activities
    TASK = "task"
    SUB_PROCESS = "subProcess"

#   Events
    START = "startEvent"
    END = "endEvent"
    INTERMEDIATE_THROW = "intermediateThrowEvent"
    INTERMEDIATE_CATCH = "intermediateCatchEvent"
    BOUNDARY = "boundaryEvent"

#   Gateways
    EXCLUSIVE = "exclusiveGateway"
    INCLUSIVE = "inclusiveGateway"
    PARALLEL = "parallelGateway"
    EVENT_BASED = "eventBasedGateway"
    COMPLEX = "complexGateway"

#   Data Objects
    DATA_OBJECT = "dataObject"


class FlowNode(FlowElement):
    """
    Class used for representing tFlowNode of BPMN 2.0 graph.
    Fields (except inherited):
    - incoming: list of IDs (strings) of incoming flows.
    - outgoing: list of IDs (strings) of outgoing flows.
    """
    incoming: List[str] = Field(default_factory=list, description="List of IDs of incoming flows")
    outgoing: List[str] = Field(default_factory=list, description="List of IDs of outgoing flows")
    process_id: str | None = Field(default=None, description="ID of the related process")
    node_type: ClassVar[NodeType] = NodeType.BASE
