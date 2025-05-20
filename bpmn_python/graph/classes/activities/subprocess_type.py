# coding=utf-8
"""
Class used for representing tSubProcess of BPMN 2.0 graph
"""
from typing import List

from pydantic import Field

from bpmn_python.graph.classes.activities.activity_type import Activity
from bpmn_python.graph.classes.flow_element_type import FlowElement
from bpmn_python.graph.classes.lane_set_type import LaneSet


class SubProcess(Activity):
    """
    Class used for representing tSubProcess of BPMN 2.0 graph
    Fields (except inherited):
    - lane_set_list: a list of LaneSet objects.
    - flow_element_list: a list of FlowElement objects.
    - triggered_by_event: a boolean value.
    """
    triggered_by_event: bool = Field(default=False, description="Indicates if subprocess is triggered by event")
    lane_set_list: List[LaneSet] = Field(default_factory=list, description="List of LaneSet objects")
    flow_element_list: List[FlowElement] = Field(default_factory=list, description="List of FlowElement objects")
