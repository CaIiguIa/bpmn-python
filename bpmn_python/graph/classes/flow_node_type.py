# coding=utf-8
"""
Class used for representing tFlowNode of BPMN 2.0 graph
"""
import bpmn_python.graph.classes.flow_element_type as flow_element_type

from typing import List
from pydantic import Field, field_validator

class FlowNode(flow_element_type.FlowElement):
    """
    Class used for representing tFlowNode of BPMN 2.0 graph.
    Fields (except inherited):
    - incoming: list of IDs (strings) of incoming flows.
    - outgoing: list of IDs (strings) of outgoing flows.
    """
    incoming: List[str] = Field(default_factory=list, description="List of IDs of incoming flows")
    outgoing: List[str] = Field(default_factory=list, description="List of IDs of outgoing flows")
