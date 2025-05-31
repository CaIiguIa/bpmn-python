# coding=utf-8
"""
Class used for representing tMessageFlow of BPMN 2.0 graph
"""
from typing import Optional

from pydantic import Field

from bpmn_python.graph.classes.base_element import BaseElement


class MessageFlow(BaseElement):
    """
    Class used for representing tMessageFlow of BPMN 2.0 graph.
    Fields:
    - name: optional string
    - source_ref: required string (ID of source node)
    - target_ref: required string (ID of target node)
    - message_ref: optional string (ID of referenced message element)
    """
    name: Optional[str] = Field(default=None, description="Optional name of the message flow")
    source_ref: str = Field(..., description="ID of source node")
    target_ref: str = Field(..., description="ID of target node")
    message_ref: Optional[str] = Field(default=None, description="ID of referenced message element")
