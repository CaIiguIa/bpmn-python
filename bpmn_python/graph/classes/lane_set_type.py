# coding=utf-8
"""
Class used for representing tSetLane of BPMN 2.0 graph
"""
from bpmn_python.graph.classes.base_element_type import BaseElement
from typing import Optional, List
from pydantic import Field, field_validator

from bpmn_python.graph.classes.lane_type import Lane

class LaneSet(BaseElement):
    """
    Class used for representing tSetLane of BPMN 2.0 graph.
    Fields (except inherited):
    - name: name of element. Must be either None (name is optional according to BPMN 2.0 XML Schema) or String.
    - lane_list: a list of Lane objects.
    """
    name: Optional[str] = Field(default=None, description="Optional name of the lane set")
    lane_list: List[Lane] = Field(default_factory=list, description="List of Lane objects")

