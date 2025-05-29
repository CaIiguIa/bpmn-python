# coding=utf-8
"""
Class used for representing tEventDefinition of BPMN 2.0 graph
"""
from enum import Enum

from pydantic import Field

from bpmn_python.graph.classes.root_element.root_element import RootElement


class EventDefinitionType(Enum):
    pass


class StartEventDefinitionType(EventDefinitionType):
    MESSAGE = "messageEventDefinition"
    TIMER = "timerEventDefinition"
    CONDITIONAL = "conditionalEventDefinition"
    SIGNAL = "signalEventDefinition"
    ESCALATION = "escalationEventDefinition"
    ERROR = "errorEventDefinition"


class EndEventDefinitionType(EventDefinitionType):
    TERMINATE = "terminateEventDefinition"
    ESCALATION = "escalationEventDefinition"
    MESSAGE = "messageEventDefinition"
    COMPENSATE = "compensateEventDefinition"
    SIGNAL = "signalEventDefinition"
    ERROR = "errorEventDefinition"


class EventDefinition(RootElement):
    """
    Class used for representing tEventDefinition of BPMN 2.0 graph.
    """
    definition_type: EventDefinitionType = Field(..., description="Definition type of the Event")
