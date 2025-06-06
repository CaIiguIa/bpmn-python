# coding=utf-8
"""
Class used for representing tActivity of BPMN 2.0 graph
"""
from typing import Optional

from pydantic import Field

from bpmn_python.graph.classes.flow_node import FlowNode, NodeType


class Activity(FlowNode):
    """
    Class used for representing tActivity of BPMN 2.0 graph.
    Fields (except inherited):
    - default: ID of default flow of gateway. Must be either None (default is optional according to BPMN 2.0 XML Schema)
    or String.
    """
    default: Optional[str] = Field(default=None, description="ID of the default flow (optional)")
