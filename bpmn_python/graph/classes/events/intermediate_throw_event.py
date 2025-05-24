# coding=utf-8
"""
Class used for representing tIntermediateThrowEvent of BPMN 2.0 graph
"""
from typing import ClassVar

from bpmn_python.graph.classes.events.event import EventType
from bpmn_python.graph.classes.events.throw_event import ThrowEvent


class IntermediateThrowEvent(ThrowEvent):
    """
    Class used for representing tIntermediateThrowEvent of BPMN 2.0 graph
    """
    node_type: ClassVar[EventType] = EventType.INTERMEDIATE_THROW
