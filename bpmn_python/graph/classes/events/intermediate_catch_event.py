# coding=utf-8
"""
Class used for representing tIntermediateCatchEvent of BPMN 2.0 graph
"""
from typing import ClassVar

from bpmn_python.graph.classes.events.catch_event import CatchEvent
from bpmn_python.graph.classes.flow_node import NodeType


class IntermediateCatchEvent(CatchEvent):
    """
    Class used for representing tIntermediateCatchEvent of BPMN 2.0 graph
    """
    node_type: ClassVar[NodeType] = NodeType.INTERMEDIATE_CATCH
