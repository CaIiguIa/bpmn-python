# coding=utf-8
"""
Class used for representing tLane of BPMN 2.0 graph
"""
from bpmn_python.graph.classes.base_element_type import BaseElement

from typing import Optional, List
from pydantic import Field, field_validator

from bpmn_python.graph.classes.lane_set_type import LaneSet

class Lane(BaseElement):
    """
    Class used for representing tLane of BPMN 2.0 graph.
    Fields (except inherited):
    - name: name of element. Must be either None (name is optional according to BPMN 2.0 XML Schema) or String.
    - flow_node_ref_list: list of strings (IDs of referenced nodes).
    - child_lane_set: optional LaneSet object.
    """
    name: Optional[str] = Field(default=None, description="Optional name of the lane")
    flow_node_ref_list: List[str] = Field(default_factory=list, description="List of flow node reference IDs")
    child_lane_set: Optional[LaneSet] = Field(default=None, description="Nested LaneSet")
