from bpmn_python.graph.classes.activities.manual_task import ManualTask
from bpmn_python.graph.classes.activities.service_task import ServiceTask
from bpmn_python.graph.classes.activities.subprocess import SubProcess
from bpmn_python.graph.classes.activities.task import Task
from bpmn_python.graph.classes.activities.user_task import UserTask
from bpmn_python.graph.classes.data_object import DataObject
from bpmn_python.graph.classes.events.boundary_event import BoundaryEvent
from bpmn_python.graph.classes.events.end_event import EndEvent
from bpmn_python.graph.classes.events.intermediate_catch_event import IntermediateCatchEvent
from bpmn_python.graph.classes.events.intermediate_throw_event import IntermediateThrowEvent
from bpmn_python.graph.classes.events.start_event import StartEvent
from bpmn_python.graph.classes.flow_node import NodeType, FlowNode
from bpmn_python.graph.classes.gateways.complex_gateway import ComplexGateway
from bpmn_python.graph.classes.gateways.event_based_gateway import EventBasedGateway
from bpmn_python.graph.classes.gateways.exclusive_gateway import ExclusiveGateway
from bpmn_python.graph.classes.gateways.inclusive_gateway import InclusiveGateway
from bpmn_python.graph.classes.gateways.parallel_gateway import ParallelGateway


def create_node(node_type: NodeType, node_id: str, process_id: str) -> FlowNode:
    """
    Factory function to create a FlowNode instance based on the specified node type.

    :param node_type: Type of the node (NodeType).
    :param node_id: Unique identifier for the node.
    :param process_id: Identifier of the process to which the node belongs.
    :return: An instance of FlowNode or its subclass based on the node_type.
    """
    match node_type:
        case NodeType.START:
            node = StartEvent(id=node_id, process_id=process_id)
        case NodeType.END:
            node = EndEvent(id=node_id, process_id=process_id)
        case NodeType.INTERMEDIATE_THROW:
            node = IntermediateThrowEvent(id=node_id, process_id=process_id)
        case NodeType.INTERMEDIATE_CATCH:
            node = IntermediateCatchEvent(id=node_id, process_id=process_id)
        case NodeType.BOUNDARY:
            node = BoundaryEvent(id=node_id, process_id=process_id)
        case NodeType.EXCLUSIVE:
            node = ExclusiveGateway(id=node_id, process_id=process_id)
        case NodeType.INCLUSIVE:
            node = InclusiveGateway(id=node_id, process_id=process_id)
        case NodeType.PARALLEL:
            node = ParallelGateway(id=node_id, process_id=process_id)
        case NodeType.COMPLEX:
            node = ComplexGateway(id=node_id, process_id=process_id)
        case NodeType.EVENT_BASED:
            node = EventBasedGateway(id=node_id, process_id=process_id)
        case NodeType.TASK:
            node = Task(id=node_id, process_id=process_id)
        case NodeType.SERVICE_TASK:
            node = ServiceTask(id=node_id, process_id=process_id)
        case NodeType.MANUAL_TASK:
            node = ManualTask(id=node_id, process_id=process_id)
        case NodeType.USER_TASK:
            node = UserTask(id=node_id, process_id=process_id)
        case NodeType.SUB_PROCESS:
            node = SubProcess(id=node_id, process_id=process_id)
        case NodeType.DATA_OBJECT:
            node = DataObject(id=node_id, process_id=process_id)
        case _:
            node = FlowNode(id=node_id, process_id=process_id)

    return node


def parse_node_type(value: str) -> NodeType:
    for member in NodeType:
        if member.value.lower() == value.lower():
            return member
    return NodeType.BASE
