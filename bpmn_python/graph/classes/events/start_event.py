# coding=utf-8
"""
Class used for representing tStartEvent of BPMN 2.0 graph
"""
from typing import ClassVar

from bpmn_python.graph.classes.events.catch_event import CatchEvent
from bpmn_python.graph.classes.events.event import EventType


class StartEvent(CatchEvent):
    """
    Class used for representing tStartEvent of BPMN 2.0 graph
    """
    node_type: ClassVar[EventType] = EventType.START
