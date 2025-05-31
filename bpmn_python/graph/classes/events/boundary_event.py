# coding=utf-8
from typing import Optional, ClassVar

from pydantic import Field

from bpmn_python.graph.classes.events.catch_event import CatchEvent
from bpmn_python.graph.classes.flow_node import NodeType


class BoundaryEvent(CatchEvent):
    """
    Class used for representing tBoundaryEvent of BPMN 2.0 graph
    """
    cancel_activity: bool = Field(
        default=True,
        description="Indicates if the activity is cancelled when the boundary event is triggered"
    )
    attached_to_ref: Optional[str] = Field(
        default=None,
        description="ID of the activity to which the boundary event is attached"
    )
    node_type: ClassVar[NodeType] = NodeType.BOUNDARY
