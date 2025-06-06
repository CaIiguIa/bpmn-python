# coding=utf-8
"""
Class used for representing tStartEvent of BPMN 2.0 graph
"""
from typing import ClassVar

from pydantic import Field

from bpmn_python.graph.classes.events.catch_event import CatchEvent
from bpmn_python.graph.classes.flow_node import NodeType


class StartEvent(CatchEvent):
    """
    Class used for representing tStartEvent of BPMN 2.0 graph
    """
    node_type: ClassVar[NodeType] = NodeType.START
    is_interrupting: bool = Field(default=True)
