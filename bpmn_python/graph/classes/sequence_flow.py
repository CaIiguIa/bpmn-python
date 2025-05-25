# coding=utf-8
"""
Class used for representing tSequenceFlow of BPMN 2.0 graph
"""
from typing import Optional

from pydantic import field_validator, Field

from bpmn_python.graph.classes.condition_expression import ConditionExpression
from bpmn_python.graph.classes.flow_element import FlowElement


class SequenceFlow(FlowElement):
    source_ref_id: str = Field(..., description="ID of the source element")
    target_ref_id: str = Field(..., description="ID of the target element")
    process_id: str = Field(..., description="ID of the related process")
    condition_expression: Optional[ConditionExpression] = Field(
        default=None,
        description="Condition expression for conditional flow. Optional."
    )
    is_immediate: Optional[bool] = Field(
        default=None,
        description="If true, indicates immediate execution of the sequence flow"
    )
    waypoints: Optional[list[tuple[float, float]]] = Field(
        default=None,
        description="List of waypoints for the sequence flow. Optional."
    )

    @field_validator('condition_expression')
    def validate_condition_expression(cls, v) -> Optional[ConditionExpression]:
        if v is not None and not isinstance(v, ConditionExpression):
            raise TypeError("condition_expression must be an instance of ConditionExpression or None")
        return v

    @field_validator('waypoints')
    def validate_waypoints(cls, v) -> Optional[list[tuple[float, float]]]:
        if v is None:
            return v

        if not isinstance(v, list) or len(v) != 2:
            raise TypeError("waypoints must be a two-element list of tuples")
        for point in v:
            if not isinstance(point, tuple) or len(point) != 2 or not all(isinstance(coord, float) for coord in point):
                raise TypeError("Each waypoint must be a tuple of two integers (x, y)")
        return v
