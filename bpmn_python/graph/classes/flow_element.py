# coding=utf-8
"""
Class used for representing tFlowElement of BPMN 2.0 graph
"""
from typing import Optional

from pydantic import Field

from bpmn_python.bpmn_python_consts import Consts
from bpmn_python.graph.classes.base_element import BaseElement


class FlowElement(BaseElement):
    """
    Class used for representing tFlowElement of BPMN 2.0 graph.
    Fields (except inherited):
    - name: name of element. Must be either None (name is optional according to BPMN 2.0 XML Schema) or String.
    """
    name: Optional[str] = Field(default=None, description="Optional name of the element")
    x: float = Field(default=Consts.default_element_x_position,
                     description="X coordinate of the element in the diagram")
    y: float = Field(default=Consts.default_element_y_position,
                     description="Y coordinate of the element in the diagram")
    width: float = Field(default=Consts.default_element_width, description="Width of the element in the diagram")
    height: float = Field(default=Consts.default_element_height, description="Height of the element in the diagram")
