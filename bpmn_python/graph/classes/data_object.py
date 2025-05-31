# coding=utf-8
from typing import ClassVar

from pydantic import Field

from bpmn_python.graph.classes.flow_node import FlowNode, NodeType


class DataObjectType(NodeType):
    DATA_OBJECT = "dataObject"


class DataObject(FlowNode):
    """
    Class used for representing tDataObject of BPMN 2.0 graph.
    """
    is_collection: bool = Field(default=False, description="Indicates if the data object is a collection")
    node_type: ClassVar[DataObjectType] = DataObjectType.DATA_OBJECT
