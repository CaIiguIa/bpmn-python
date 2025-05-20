# coding=utf-8
"""
Class used for representing tBaseElement of BPMN 2.0 graph
"""

from typing import Optional

from pydantic import BaseModel, Field


class BaseElement(BaseModel):
    """
    Class used for representing tBaseElement of BPMN 2.0 graph.
    Fields:
    - id: an ID of element. Must be either None (ID is optional according to BPMN 2.0 XML Schema) or String.
    """
    id: Optional[str] = Field(default=None)
