# coding=utf-8
"""
Class used for representing tCallableElement of BPMN 2.0 graph
"""
from typing import Optional

from pydantic import Field

from bpmn_python.graph.classes.root_element.root_element_type import RootElement


class CallableElement(RootElement):
    """
    Class used for representing tCallableElement of BPMN 2.0 graph.
    """
    name: Optional[str] = Field(default=None, description="Optional name of the callable element")
