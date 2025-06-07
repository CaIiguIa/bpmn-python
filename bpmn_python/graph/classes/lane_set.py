# coding=utf-8
"""
Class used for representing tSetLane of BPMN 2.0 graph
"""
from typing import Optional, List

from pydantic import Field

from bpmn_python.bpmn_python_consts import Consts
from bpmn_python.graph.classes.base_element import BaseElement


class LaneSet(BaseElement):
    """
    Class used for representing tSetLane of BPMN 2.0 graph.
    Fields (except inherited):
    - name: name of element. Must be either None (name is optional according to BPMN 2.0 XML Schema) or String.
    - lane_list: a list of Lane objects.
    """
    name: Optional[str] = Field(default=None, description="Optional name of the lane set")
    lanes: dict[str, "Lane"] = Field(default_factory=dict,
                                     description="Dictionary of Lane objects. Lane ID is used as a key.")


class Lane(BaseElement):
    """
    Class used for representing tLane of BPMN 2.0 graph.
    Fields (except inherited):
    - name: name of element. Must be either None (name is optional according to BPMN 2.0 XML Schema) or String.
    - flow_node_ref_list: list of strings (IDs of referenced nodes).
    - child_lane_set: optional LaneSet object.
    """
    name: Optional[str] = Field(default=None, description="Optional name of the lane")
    flow_node_refs: List[str] = Field(default_factory=list, description="List of flow node reference IDs")
    child_lane_set: Optional[LaneSet] = Field(default=None, description="Nested LaneSet")

    x: float = Field(default=Consts.default_element_x_position,
                     description="X coordinate of the lane in the diagram. Its value in xml is stored in a separate element.")
    y: float = Field(default=Consts.default_element_y_position,
                     description="Y coordinate of the lane in the diagram. Its value in xml is stored in a separate element.")
    width: float = Field(default=Consts.default_element_width,
                         description="Width of the lane in the diagram. Its value in xml is stored in a separate element.")
    height: float = Field(default=Consts.default_element_height,
                          description="Height of the lane in the diagram. Its value in xml is stored in a separate element.")
    is_horizontal: bool = Field(default=Consts.default_is_horizontal,
                                description="Indicates if the lane is horizontal or vertical. Its value in xml is stored in a separate element.")


Lane.model_rebuild()
LaneSet.model_rebuild()
