# coding=utf-8
"""
Class used for representing tUserTask of BPMN 2.0 graph
"""
from typing import ClassVar

from bpmn_python.graph.classes.activities.activity import Activity
from bpmn_python.graph.classes.activities.task import Task
from bpmn_python.graph.classes.flow_node import NodeType


class UserTask(Task):
    """
    Class used for representing tUserTask of BPMN 2.0 graph
    """
    node_type: ClassVar[NodeType] = NodeType.USER_TASK
