# coding=utf-8
"""
Class used for representing tProcess of BPMN 2.0 graph
"""
from typing import List, Literal

from pydantic import Field

from bpmn_python.graph.classes.flow_element_type import FlowElement
from bpmn_python.graph.classes.lane_set_type import LaneSet
from bpmn_python.graph.classes.root_element.callable_element_type import CallableElement


class Process(CallableElement):
    """
    Class used for representing tProcess of BPMN 2.0 graph.
    """

    process_type: Literal["None", "Public", "Private"] = Field(default="None", description="Type of process")
    is_closed: bool = Field(default=False, description="Indicates if the process is closed")
    is_executable: bool = Field(default=False, description="Indicates if the process is executable")
    lane_set_list: List[LaneSet] = Field(default_factory=list, description="List of LaneSet objects")
    flow_element_list: List[FlowElement] = Field(default_factory=list, description="List of FlowElement objects")
