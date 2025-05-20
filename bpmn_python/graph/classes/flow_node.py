# coding=utf-8
"""
Class used for representing tFlowNode of BPMN 2.0 graph
"""
from typing import List

from pydantic import Field

import bpmn_python.graph.classes.flow_element as flow_element_type


class FlowNode(flow_element_type.FlowElement):
    """
    Class used for representing tFlowNode of BPMN 2.0 graph.
    Fields (except inherited):
    - incoming: list of IDs (strings) of incoming flows.
    - outgoing: list of IDs (strings) of outgoing flows.
    """
    incoming: List[str] = Field(default_factory=list, description="List of IDs of incoming flows")
    outgoing: List[str] = Field(default_factory=list, description="List of IDs of outgoing flows")
