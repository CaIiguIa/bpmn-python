# coding=utf-8
"""
Class used for representing tSubProcess of BPMN 2.0 graph
"""
from typing import List, ClassVar

from pydantic import Field, field_validator

from bpmn_python.graph.classes.activities.activity import Activity, ActivityType
from bpmn_python.graph.classes.flow_element import FlowElement
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
    node_type: ClassVar[ActivityType] = ActivityType.SUB_PROCESS

    @classmethod
    @field_validator("is_expanded", mode="before")
    def convert_str_to_bool(cls, value):
        if isinstance(value, str):
            if value.strip().lower() in {"true", "1", "yes", "on"}:
                return True
            elif value.strip().lower() in {"false", "0", "no", "off"}:
                return False
            raise ValueError(
                "is_expanded must be a boolean value or a string that can be converted to boolean"
            )
        return value
