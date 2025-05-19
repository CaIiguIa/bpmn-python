# coding=utf-8
"""
Class used for representing tSequenceFlow of BPMN 2.0 graph
"""
from bpmn_python.graph.classes.condition_expression_type import ConditionExpression
from bpmn_python.graph.classes.flow_element_type import FlowElement

from typing import Optional
from pydantic import field_validator

class SequenceFlow(FlowElement):
    source_ref: str
    target_ref: str
    condition_expression: Optional[ConditionExpression] = None
    is_immediate: Optional[bool] = None

    @field_validator('condition_expression')
    def validate_condition_expression(cls, v):
        if v is not None and not isinstance(v, ConditionExpression):
            raise TypeError("condition_expression must be an instance of ConditionExpression or None")
        return v
