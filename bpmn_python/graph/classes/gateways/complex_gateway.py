# coding=utf-8
"""
Class used for representing tComplexGateway of BPMN 2.0 graph
"""
from typing import ClassVar

from bpmn_python.graph.classes.flow_node import NodeType
from bpmn_python.graph.classes.gateways.gateway import Gateway


class ComplexGateway(Gateway):
    """
    Class used for representing tComplexGateway of BPMN 2.0 graph
    """
    node_type: ClassVar[NodeType] = NodeType.COMPLEX
