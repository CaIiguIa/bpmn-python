# coding=utf-8
"""
Class used for representing tParticipant of BPMN 2.0 graph
"""
from typing import Optional

from pydantic import Field

from bpmn_python.bpmn_python_consts import Consts
from bpmn_python.graph.classes.flow_element import FlowElement


class Participant(FlowElement):
    """
    Class used for representing tParticipant of BPMN 2.0 graph
    Fields (except inherited):
    - name: name of element. Must be either None (name is optional according to BPMN 2.0 XML Schema) or String.
    - process_ref: an ID of referenced message element. Must be either None (process_ref is optional according to
    BPMN 2.0 XML Schema) or String.
    """
    process_ref: Optional[str] = Field(default=None)
    is_horizontal: bool = Field(default=Consts.default_is_horizontal,
                                description="Indicates if the Participant is horizontal or vertical")
