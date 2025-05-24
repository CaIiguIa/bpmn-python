# coding=utf-8
"""
Class used for representing tTask of BPMN 2.0 graph
"""
from typing import ClassVar

from bpmn_python.graph.classes.activities.activity import Activity, ActivityType


class Task(Activity):
    """
    Class used for representing tTask of BPMN 2.0 graph
    """
    node_type: ClassVar[ActivityType] = ActivityType.TASK
