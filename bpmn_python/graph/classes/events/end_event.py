# coding=utf-8
"""
Class used for representing tEndEvent of BPMN 2.0 graph
"""
from typing import ClassVar

from bpmn_python.graph.classes.events.throw_event import ThrowEvent
from bpmn_python.graph.classes.flow_node import NodeType


class EndEvent(ThrowEvent):
    """
    Class used for representing tEndEvent of BPMN 2.0 graph
    """
    node_type: ClassVar[NodeType] = NodeType.END
