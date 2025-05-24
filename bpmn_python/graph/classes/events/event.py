# coding=utf-8
"""
Class used for representing tEvent of BPMN 2.0 graph
"""
from bpmn_python.graph.classes.flow_node import FlowNode, NodeType


class Event(FlowNode):
    """
    Class used for representing tEvent of BPMN 2.0 graph
    """

class EventType(NodeType):
    START = "startEvent"
    END = "endEvent"
    INTERMEDIATE_THROW = "intermediateThrowEvent"
    INTERMEDIATE_CATCH = "intermediateCatchEvent"