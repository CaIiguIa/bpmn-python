# coding=utf-8
"""
Class used for representing tSubProcess of BPMN 2.0 graph
"""
from typing import List, ClassVar

from pydantic import Field

from bpmn_python.graph.classes.activities.activity import Activity
from bpmn_python.graph.classes.flow_element import FlowElement
from bpmn_python.graph.classes.flow_node import NodeType
from bpmn_python.graph.classes.lane_set import LaneSet


class SubProcess(Activity):
    """
    Class used for representing tSubProcess of BPMN 2.0 graph
    Fields (except inherited):
    - lane_set_list: a list of LaneSet objects.
    - flow_element_list: a list of FlowElement objects.
    - triggered_by_event: a boolean value.
    - is_expanded: a boolean value indicating if the subprocess is expanded (default is True).
    """
    triggered_by_event: bool = Field(default=False, description="Indicates if subprocess is triggered by event")
    lane_set_list: List[LaneSet] = Field(default_factory=list, description="List of LaneSet objects")
    flow_element_list: List[FlowElement] = Field(default_factory=list, description="List of FlowElement objects")
    is_expanded: bool = Field(default=True, description="Indicates if the subprocess is expanded (default is True)")
    node_type: ClassVar[NodeType] = NodeType.SUB_PROCESS
