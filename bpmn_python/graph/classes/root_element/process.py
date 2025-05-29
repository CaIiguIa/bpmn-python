# coding=utf-8
"""
Class used for representing tProcess of BPMN 2.0 graph
"""
from enum import Enum
from typing import List

from pydantic import Field

from bpmn_python.graph.classes.flow_element import FlowElement
from bpmn_python.graph.classes.lane_set import LaneSet
from bpmn_python.graph.classes.root_element.callable_element import CallableElement


class Process(CallableElement):
    """
    Class used for representing tProcess of BPMN 2.0 graph.
    """

    process_type: "ProcessType" = Field(default="None", description="Type of process")
    is_closed: bool = Field(default=False, description="Indicates if the process is closed")
    is_executable: bool = Field(default=False, description="Indicates if the process is executable")
    lane_set_list: List[LaneSet] = Field(default_factory=list, description="List of LaneSet objects")
    flow_element_list: List[FlowElement] = Field(default_factory=list, description="List of FlowElement objects")


class ProcessType(Enum):
    NONE = "None",
    PUBLIC = "Public",
    PRIVATE = "Private"

    @classmethod
    def parse(cls, value: str) -> "ProcessType":
        """
        Parse a string value to a ProcessType enum member.

        :param value: The string value to parse.
        :return: Corresponding ProcessType enum member.
        """
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Invalid ProcessType value: {value}")
