# coding=utf-8
"""
Class used for representing tParticipant of BPMN 2.0 graph
"""
import graph.classes.base_element_type as base_element
from typing import Optional
from pydantic import Field

class Participant(base_element.BaseElement):
    """
    Class used for representing tParticipant of BPMN 2.0 graph
    Fields (except inherited):
    - name: name of element. Must be either None (name is optional according to BPMN 2.0 XML Schema) or String.
    - process_ref: an ID of referenced message element. Must be either None (process_ref is optional according to
    BPMN 2.0 XML Schema) or String.
    """
    name: Optional[str] = Field(default=None)
    process_ref: Optional[str] = Field(default=None)