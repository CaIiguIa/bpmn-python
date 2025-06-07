# coding=utf-8
"""
Class used for representing tTask of BPMN 2.0 graph
"""
from typing import ClassVar

from bpmn_python.graph.classes.activities.activity import Activity
from bpmn_python.graph.classes.flow_node import NodeType


class Task(Activity):
    """
    Class used for representing tTask of BPMN 2.0 graph
    """
    node_type: ClassVar[NodeType] = NodeType.TASK
