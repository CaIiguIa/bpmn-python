# coding=utf-8
"""
Class used for representing tFlowElement of BPMN 2.0 graph
"""
from typing import Optional

from pydantic import Field

from bpmn_python.graph.classes.base_element import BaseElement


class FlowElement(BaseElement):
    """
    Class used for representing tFlowElement of BPMN 2.0 graph.
    Fields (except inherited):
    - name: name of element. Must be either None (name is optional according to BPMN 2.0 XML Schema) or String.
    """
    name: Optional[str] = Field(default=None, description="Optional name of the element")
