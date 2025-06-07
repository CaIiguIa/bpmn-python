# coding=utf-8
"""
Class used for representing tEventDefinition of BPMN 2.0 graph
"""
from enum import Enum

from pydantic import Field

from bpmn_python.graph.classes.root_element.root_element import RootElement


class EventDefinitionType(Enum):
    MESSAGE = "messageEventDefinition"
    TIMER = "timerEventDefinition"
    CONDITIONAL = "conditionalEventDefinition"
    SIGNAL = "signalEventDefinition"
    ESCALATION = "escalationEventDefinition"
    TERMINATE = "terminateEventDefinition"
    COMPENSATE = "compensateEventDefinition"
    ERROR = "errorEventDefinition"


class StartEventDefinitionTypes:
    @staticmethod
    def getTypes() -> set[EventDefinitionType]:
        return {
            EventDefinitionType.MESSAGE,
            EventDefinitionType.TIMER,
            EventDefinitionType.CONDITIONAL,
            EventDefinitionType.SIGNAL,
            EventDefinitionType.ESCALATION
        }


class EndEventDefinitionTypes:
    @staticmethod
    def getTypes() -> set[EventDefinitionType]:
        return {
            EventDefinitionType.MESSAGE,
            EventDefinitionType.SIGNAL,
            EventDefinitionType.ESCALATION,
            EventDefinitionType.TERMINATE,
            EventDefinitionType.COMPENSATE,
            EventDefinitionType.ERROR
        }


class IntermediateThrowEventDefinitionTypes:
    @staticmethod
    def getTypes() -> set[EventDefinitionType]:
        return {
            EventDefinitionType.MESSAGE,
            EventDefinitionType.SIGNAL,
            EventDefinitionType.ESCALATION,
            EventDefinitionType.COMPENSATE
        }


class IntermediateCatchEventDefinitionTypes:
    @staticmethod
    def getTypes() -> set[EventDefinitionType]:
        return {
            EventDefinitionType.MESSAGE,
            EventDefinitionType.TIMER,
            EventDefinitionType.SIGNAL,
            EventDefinitionType.CONDITIONAL,
            EventDefinitionType.ESCALATION
        }


class BoundaryEventDefinitionTypes:
    @staticmethod
    def getTypes() -> set[EventDefinitionType]:
        return {
            EventDefinitionType.MESSAGE,
            EventDefinitionType.TIMER,
            EventDefinitionType.SIGNAL,
            EventDefinitionType.CONDITIONAL,
            EventDefinitionType.ESCALATION,
            EventDefinitionType.ERROR
        }


class EventDefinition(RootElement):
    """
    Class used for representing tEventDefinition of BPMN 2.0 graph.
    """
    definition_type: EventDefinitionType = Field(..., description="Definition type of the Event")
