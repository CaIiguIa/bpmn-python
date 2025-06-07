# coding=utf-8
"""
Class used for representing tCatchEvent of BPMN 2.0 graph
"""

from typing import List

from pydantic import Field

from bpmn_python.graph.classes.events.event import Event
from bpmn_python.graph.classes.root_element.event_definition import EventDefinition


class CatchEvent(Event):
    """
    Class used for representing tCatchEvent of BPMN 2.0 graph
    Fields (except inherited):
    - parallel_multiple: a boolean value. Default is False.
    - event_definition_list: list of EventDefinition objects.
    """
    parallel_multiple: bool = Field(default=False, description="Indicates if event is parallel multiple")
    event_definition_list: List[EventDefinition] = Field(
        default_factory=list,
        description="Optional list of EventDefinition objects"
    )
