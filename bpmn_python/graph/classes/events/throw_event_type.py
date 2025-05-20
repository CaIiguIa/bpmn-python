# coding=utf-8
"""
Class used for representing tThrowEvent of BPMN 2.0 graph
"""
from typing import List

from pydantic import Field

from bpmn_python.graph.classes.events.event_type import Event
from bpmn_python.graph.classes.root_element.event_definition_type import EventDefinition


class ThrowEvent(Event):
    """
    Class used for representing tThrowEvent of BPMN 2.0 graph
    Fields (except inherited):
    - event_definition_list: a list of EventDefinition objects.
    """
    event_definition_list: List[EventDefinition] = Field(
        default_factory=list,
        description="Optional list of EventDefinition objects"
    )
