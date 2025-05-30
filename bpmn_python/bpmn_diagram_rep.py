# coding=utf-8
"""
Package with BPMNDiagramGraph - graph representation of BPMN diagram
"""
import uuid
from typing import Dict

import networkx as nx
from pydantic import BaseModel, Field

import bpmn_python.bpmn_diagram_exception as bpmn_exception
import bpmn_python.bpmn_diagram_export as bpmn_export
import bpmn_python.bpmn_diagram_import as bpmn_import
import bpmn_python.bpmn_process_csv_export as bpmn_csv_export
import bpmn_python.bpmn_process_csv_import as bpmn_csv_import
import bpmn_python.bpmn_python_consts as consts
from bpmn_python.bpmn_python_consts import Consts
from bpmn_python.graph.classes.activities.activity import ActivityType
from bpmn_python.graph.classes.activities.subprocess import SubProcess
from bpmn_python.graph.classes.events.end_event import EndEvent
from bpmn_python.graph.classes.events.event import EventType
from bpmn_python.graph.classes.events.start_event import StartEvent
from bpmn_python.graph.classes.flow_node import FlowNode, NodeType
from bpmn_python.graph.classes.gateways.gateway import GatewayType, GatewayDirection, Gateway
from bpmn_python.graph.classes.message_flow import MessageFlow
from bpmn_python.graph.classes.participant import Participant
from bpmn_python.graph.classes.root_element.event_definition import StartEventDefinitionType, EndEventDefinitionType, \
    EventDefinition
from bpmn_python.graph.classes.root_element.process import Process, ProcessType
from bpmn_python.graph.classes.sequence_flow import SequenceFlow
from bpmn_python.node_creator import create_node, parse_node_type


class BpmnDiagramGraph(BaseModel):
    """
    Class BPMNDiagramGraph implements simple inner representation of BPMN 2.0 diagram,
    based on NetworkX graph implementation

    Fields:

    * diagram_graph - networkx.Graph object, stores elements of BPMN diagram as nodes. Each edge of graph represents
        sequenceFlow element. Edges are identified by IDs of nodes connected by edge. IDs are passed as edge parameters,
    * sequence_flows - dictionary (associative list) of sequence flows existing in diagram.
        Key attribute is sequenceFlow ID, value is a dictionary consisting three key-value pairs: "name" (sequence flow
        name), "sourceRef" (ID of node, that is a flow source) and "targetRef" (ID of node, that is a flow target),
    * collaboration - a dictionary that contains two dictionaries:
        * "messageFlows" - dictionary (associative list) of message flows existing in diagram. Key attribute is
            messageFlow ID, value is a dictionary consisting three key-value pairs: "name" (message flow name),
            "sourceRef" (ID of node, that is a flow source) and "targetRef" (ID of node, that is a flow target),
        * "participants" - dictionary (associative list) of participants existing in diagram. Key attribute is
            participant ID, value is a dictionary consisting participant attributes,
    * process_elements_dictionary - dictionary that holds attribute values for imported 'process' elements. 
        Key is an ID of process, value is a dictionary of all process attributes,

    * diagram_attributes - dictionary that contains BPMN diagram element attributes,
    * plane_attributes - dictionary that contains BPMN plane element attributes.
    """

    sequence_flows: Dict[str, SequenceFlow] = Field(
        default_factory=dict,
        description="Mapping of sequence flow IDs to SequenceFlow objects."
    )
    nodes: Dict[str, FlowNode] = Field(
        default_factory=dict,
        description="Mapping of flow nodes IDs to FlowNode objects."
    )
    process_elements: Dict[str, Process] = Field(
        default_factory=dict,
        description="Mapping of process IDs to Process objects with their attributes."
    )
    diagram_attributes: Dict[str, str] = Field(
        default_factory=dict,
        description="Attributes of the BPMNDiagram element."
    )
    plane_attributes: Dict[str, str] = Field(
        default_factory=dict,
        description="Attributes of the BPMNPlane element."
    )
    message_flows: Dict[str, MessageFlow] = Field(
        default_factory=dict,
        description="Mapping of message flow IDs to MessageFlow objects."
    )
    participants: Dict[str, Participant] = Field(
        default_factory=dict,
        description="Mapping of participant IDs to Participant objects."
    )

    def load_diagram_from_xml_file(self, filepath: str) -> None:
        """
        Reads an XML file from given filepath and maps it into inner representation of BPMN diagram.
        Returns an instance of BPMNDiagramGraph class.

        Args:
             filepath (str): XML filepath.
        """

        bpmn_import.BpmnDiagramGraphImport.load_diagram_from_xml(filepath, self)

    def export_xml_file(self, directory: str, filename: str) -> None:
        """
        Exports diagram inner graph to BPMN 2.0 XML file (with Diagram Interchange data).

        Args:
            directory (str): output directory,
            filename (str): output file name.
        """
        bpmn_export.BpmnDiagramGraphExport.export_xml_file(directory, filename, self)

    def export_xml_file_no_di(self, directory: str, filename: str):
        """
        Exports diagram inner graph to BPMN 2.0 XML file (without Diagram Interchange data).

        Args:
            directory (str): output directory,
            filename (str): output file name.
        """
        bpmn_export.BpmnDiagramGraphExport.export_xml_file_no_di(directory, filename, self)

    def load_diagram_from_csv_file(self, filepath: str) -> None:
        """
        Reads an CSV file from given filepath and maps it into inner representation of BPMN diagram.
        Returns an instance of BPMNDiagramGraph class.

        Args:
            filepath (str): CSV filepath.
        """

        bpmn_csv_import.BpmnDiagramGraphCSVImport.load_diagram_from_csv(filepath, self)

    def export_csv_file(self, directory: str, filename: str) -> None:
        """
        Exports diagram inner graph to BPMN 2.0 XML file (with Diagram Interchange data).

        Args:
            directory (str): output directory,
            filename (str): output file name.
        """
        bpmn_csv_export.BpmnDiagramGraphCsvExport.export_process_to_csv(self, directory, filename)

    # Querying methods
    def get_nodes(self, node_type: str = "") -> list[tuple[str, FlowNode]]:
        """
        Returns all nodes of requested type. If no type is provided by user, all nodes in BPMN diagram graph are returned.

        Args:
            node_type (str): valid BPMN XML tag name (e.g. 'task', 'sequenceFlow'). Returns all nodes if empty.

        Returns:
            list of tuples: first element of each tuple is node ID, second element is a FlowNode object.
        """
        tmp_nodes = list(self.nodes.items())
        if node_type == "":
            return tmp_nodes
        else:
            nodes = []
            for node_id, node in tmp_nodes:
                if node.node_type == node_type:
                    nodes.append((node_id, node))
            return nodes

    def get_nodes_list_by_process_id(self, process_id: str) -> list[tuple[str, FlowNode]]:
        """
        Returns all nodes connected to a process with given ID.

        Args:
            process_id (str): ID of parent process element.

        Returns:
            list of tuples: first element of each tuple is node ID, second element is a FlowNode object.
        """
        nodes = []
        for node_id, node in self.nodes.items():
            if node.process_id == process_id:
                nodes.append((node_id, node))
        return nodes

    def get_node_by_id(self, node_id: str) -> tuple[str, FlowNode]:
        """
        Returns a node with requested ID.

        Args:
            node_id (str): ID of node.

        Returns:
            tuple: node ID and FlowNode object
        """

        node = self.nodes[node_id]
        return node.id, node

    def get_nodes_id_list_by_type(self, node_type: str) -> list[str]:
        """
        Return a list of node's id by requested type.

        Args:
            node_type (str): valid BPMN XML tag name (e.g. 'task', 'sequenceFlow').

        Returns:
            list: list of node's id
        """
        if node_type == "":
            return list(self.nodes.keys())
        else:
            nodes = []
            for node_id, node in list(self.nodes.items()):
                if node.node_type == node_type:
                    nodes.append(node_id)
            return nodes

    def get_nodes_positions(self) -> dict[str, tuple[float, float]]:
        """
        Returns all nodes positions in the layout.

        Returns:
            tuple: A dictionary with nodes as keys and positions (tuples containing two floats) as values
        """
        nodes = self.get_nodes()
        output = {}
        for node_id, node in nodes:
            output[node_id] = (node.x, node.y)
        return output

    def get_flows(self) -> list[tuple[str, str, SequenceFlow]]:
        """
        Returns all graph edges (process flows).

        Returns:
            List of tuples: first value of each tuple is Source Node ID, second value is Target Node ID, third - a SequenceFlow Object.
        """
        flows = []
        for _, flow in self.sequence_flows.items():
            flows.append((flow.source_ref_id, flow.target_ref_id, flow))

        return flows

    def get_flow_by_id(self, flow_id: str) -> tuple[str, str, SequenceFlow] | None:
        """
        Returns an edge (flow) with requested ID.

        Args:
            flow_id (str): ID of flow.

        Returns:
            tuple: first value is Source Node ID, second value is Target Node ID, third - a SequenceFlow Object.
        """
        flow = self.sequence_flows[flow_id]
        if flow is None:
            return None

        return flow.source_ref_id, flow.target_ref_id, flow

    def get_flows_list_by_process_id(self, process_id: str) -> list[tuple[str, str, SequenceFlow]]:
        """
        Returns list of flows connected to a process with given ID.

        Args:
            process_id (str): ID of parent process element.

        Returns:
            List of tuples: first value of each tuple is Source Node ID, second value is Target Node ID, third - a SequenceFlow Object.
        """
        flows = []
        for _, flow in self.sequence_flows.items():
            if flow.process_id == process_id:
                flows.append((flow.source_ref_id, flow.target_ref_id, flow))

        return flows

    # Diagram creating methods
    def create_new_diagram_graph(self, diagram_name: str = "") -> None:
        """
        Initializes a new BPMN diagram and sets up a basic diagram attributes.

        Args:
            diagram_name (str): name of diagram.
        """
        self.__init__()
        diagram_id = Consts.id_prefix + str(uuid.uuid4())

        self.diagram_attributes[consts.Consts.id] = diagram_id
        self.diagram_attributes[consts.Consts.name] = diagram_name

        # TODO: make sure that it initializes new diagram properly

    def add_process_to_diagram(self,
                               process_name: str = "",
                               process_is_closed: bool = False,
                               process_is_executable: bool = False,
                               process_type: ProcessType = "None") -> str:
        """
        Adds a new process to diagram and corresponding participant
            process, diagram and plane

        Args:
            process_name (str): name of process
            process_is_closed (bool): is process closed
            process_is_executable (bool): is process executable
            process_type (str): type of process

        Returns:
            str: ID of created process
        """
        plane_id = Consts.id_prefix + str(uuid.uuid4())
        process_id = Consts.id_prefix + str(uuid.uuid4())

        process = Process(
            id=process_id,
            name=process_name,
            process_type=process_type,
            is_closed=process_is_closed,
            is_executable=process_is_executable,
            lane_set_list=[],
            flow_element_list=[]
        )

        self.process_elements[process_id] = process

        self.plane_attributes[consts.Consts.id] = plane_id
        self.plane_attributes[consts.Consts.bpmn_element] = process_id
        return process_id

    def add_modify_flow_node_to_diagram(self,
                                        process_id: str,
                                        node_type: NodeType | str,
                                        name: str,
                                        node_id: str = None,
                                        modify: bool = False) -> tuple[str, FlowNode]:
        """
        Helper function that adds a new Flow Node to diagram. It is used to add a new node of specified type. If modify
        is set to True, it will modify existing node with given node_id.

        Args:
            process_id (str): ID of parent process.
            node_type (str): type of node.
            name (str): name of node.
            node_id (str): ID of node. Default value - None.
            modify (bool): Whether to modify existing node or create a new one. Default value - False.

        Returns:
            tuple: first value is node ID, second - a reference to created object.
        """
        if node_id is None:
            node_id = Consts.id_prefix + str(uuid.uuid4())

        if isinstance(node_type, str):
            node_type = parse_node_type(node_type)

        if not modify:
            new_node = create_node(node_type, node_id, process_id)
            self.nodes[node_id] = new_node

            # self.diagram_graph.add_node(node_id)
            # self.diagram_graph.nodes[node_id][consts.Consts.id] = node_id
            # self.diagram_graph.nodes[node_id][consts.Consts.incoming_flow] = []
            # self.diagram_graph.nodes[node_id][consts.Consts.outgoing_flow] = []
            # self.diagram_graph.nodes[node_id][consts.Consts.type] = node_type

        node = self.nodes[node_id]
        node.name = name
        node.process_id = process_id

        # self.diagram_graph.nodes[node_id][consts.Consts.process] = process_id
        # self.diagram_graph.nodes[node_id][consts.Consts.node_name] = name
        # self.diagram_graph.nodes[node_id][consts.Consts.width] = "100"
        # self.diagram_graph.nodes[node_id][consts.Consts.height] = "100"
        # self.diagram_graph.nodes[node_id][consts.Consts.x] = "100"
        # self.diagram_graph.nodes[node_id][consts.Consts.y] = "100"
        return node_id, node

    def add_modify_task_to_diagram(self, process_id: str, task_name: str = "", node_id: str = None) -> tuple:
        """
        Add or modify a Task element to BPMN diagram or modifies existing one if node_id matches existing task.

        Args:
            process_id (str): ID of parent process,
            task_name (str): Name of task,
            node_id (str): ID of node. Default value - None.

        Returns:
            tuple: first value is task ID, second - a reference to created object.
        """
        modify_task = False
        _, existing_node = self.get_node_by_id(node_id=node_id)

        if existing_node and existing_node.node_type == ActivityType.TASK:
            modify_task = True

        if existing_node and not existing_node.node_type == ActivityType.TASK:
            raise bpmn_exception.BpmnNodeTypeError("Node with given ID is not a task")

        return self.add_modify_flow_node_to_diagram(process_id=process_id,
                                                    node_type=consts.Consts.task,
                                                    name=task_name,
                                                    node_id=node_id,
                                                    modify=modify_task)

    def add_subprocess_to_diagram(self,
                                  process_id: str,
                                  subprocess_name: str = "",
                                  is_expanded: bool = False,
                                  triggered_by_event: bool = False,
                                  node_id: str = None) -> tuple:
        """
        Adds a SubProcess element to BPMN diagram.

        Args:
            process_id (str): ID of parent process.
            subprocess_name (str): Name of subprocess.
            is_expanded (bool): is subprocess expanded.
            triggered_by_event (bool): is triggered by event.
            node_id (str): ID of node. Default value - None.

        Returns:
            tuple: first value is subprocess ID, second - a reference to created object.
        """
        subprocess_id, subprocess = self.add_modify_flow_node_to_diagram(
            process_id=process_id,
            node_type=ActivityType.SUB_PROCESS,
            name=subprocess_name,
            node_id=node_id,
            modify=False)

        if not isinstance(subprocess, SubProcess):
            raise bpmn_exception.BpmnNodeTypeError("Node with given ID is not a subprocess")
        subprocess.is_expanded = is_expanded
        subprocess.triggered_by_event = triggered_by_event

        # self.diagram_graph.nodes[subprocess_id][consts.Consts.is_expanded] = str(is_expanded).lower()
        # self.diagram_graph.nodes[subprocess_id][consts.Consts.triggered_by_event] = str(triggered_by_event).lower()
        return subprocess_id, subprocess

    def add_modify_start_event_to_diagram(self,
                                          process_id: str,
                                          start_event_name: str = "",
                                          start_event_definition: StartEventDefinitionType = None,
                                          parallel_multiple: bool = False,
                                          is_interrupting: bool = True,
                                          node_id: str = None) -> tuple:
        """
        Add or modify a StartEvent element to BPMN diagram. If node_id matches existing start event, it will be modified.

        Args:
            process_id (str): ID of parent process,
            start_event_name (str): Name of start event,
            start_event_definition (StartEventDefinitionType): type of start event,
            parallel_multiple (bool): is parallel multiple,
            is_interrupting (bool): is interrupting,
            node_id (str): ID of node. Default value - None.

        Returns:
            tuple: first value is start event ID, second - a reference to created object.
        """
        modify_start_event = False

        _, existing_node = self.get_node_by_id(node_id=node_id)
        if existing_node and existing_node.node_type == EventType.START:
            modify_start_event = True

        if existing_node and not existing_node.node_type == EventType.START:
            raise bpmn_exception.BpmnNodeTypeError("Node with given ID is not a start event")

        start_event_id, start_event = self.add_modify_flow_node_to_diagram(
            process_id=process_id,
            node_type=EventType.START,
            name=start_event_name,
            node_id=node_id,
            modify=modify_start_event)

        if not isinstance(start_event, StartEvent):
            raise bpmn_exception.BpmnNodeTypeError("Node with given ID is not a start event")

        start_event.parallel_multiple = parallel_multiple
        start_event.is_interrupting = is_interrupting

        # self.diagram_graph.nodes[start_event_id][consts.Consts.parallel_multiple] = str(parallel_multiple).lower()
        # self.diagram_graph.nodes[start_event_id][consts.Consts.is_interrupting] = str(is_interrupting).lower()

        event_def_list = []
        if start_event_definition:
            event_def_id = Consts.id_prefix + str(uuid.uuid4())
            event_def = EventDefinition(id=event_def_id, definition_type=start_event_definition)
            event_def_list.append(event_def)

        start_event.event_definition_list = event_def_list
        # self.diagram_graph.nodes[start_event_id][consts.Consts.event_definitions] = event_def_list

        return start_event_id, start_event

    def add_modify_end_event_to_diagram(self,
                                        process_id: str,
                                        end_event_name: str = "",
                                        end_event_definition: EndEventDefinitionType = None,
                                        node_id: str = None) -> tuple:
        """
        Add or modify an EndEvent element to BPMN diagram. If node_id matches existing end event, it will be modified.

        Args:
            process_id (str): ID of parent process,
            end_event_name (str): Name of end event,
            end_event_definition (EndEventDefinitionType): type of end event,
            node_id (str): ID of node. Default value - None.

        Returns:
            tuple: first value is end event ID, second - a reference to created object.
        """
        modify_end_event = False

        _, existing_node = self.get_node_by_id(node_id=node_id)
        if existing_node and existing_node.node_type == EventType.END:
            modify_end_event = True

        if existing_node and not existing_node.node_type == EventType.END:
            raise bpmn_exception.BpmnNodeTypeError("Node with given ID is not an end event")

        end_event_id, end_event = self.add_modify_flow_node_to_diagram(
            process_id=process_id,
            node_type=consts.Consts.end_event,
            name=end_event_name,
            node_id=node_id,
            modify=modify_end_event)

        if not isinstance(end_event, EndEvent):
            raise bpmn_exception.BpmnNodeTypeError("Node with given ID is not a start event")

        event_def_list = []
        if end_event_definition:
            event_def_id = Consts.id_prefix + str(uuid.uuid4())
            event_def = EventDefinition(id=event_def_id, definition_type=end_event_definition)
            event_def_list.append(event_def)

        end_event.event_definition_list = event_def_list
        # self.diagram_graph.nodes[end_event_id][consts.Consts.event_definitions] = event_def_list
        return end_event_id, end_event

    def add_modify_gateway_to_diagram(self,
                                      process_id: str,
                                      gateway_type: GatewayType,
                                      gateway_name: str = "",
                                      gateway_direction: GatewayDirection = GatewayDirection.UNSPECIFIED,
                                      node_id: str = None,
                                      default_target_id: str = None) -> tuple:
        """
        Add or modify a gateway element to BPMN diagram. If node_id matches existing gateway, it will be modified.

        Args:
            process_id (str): ID of parent process,
            gateway_type (GatewayType): type of gateway,
            gateway_name (str): name of gateway,
            gateway_direction (GatewayDirection): direction of gateway,
            node_id (str): ID of node. Default value - None.
            default_target_id (str): ID of default target node. Default value - None.

        Returns:
            tuple: first value is gateway ID, second - a reference to created object.
        """
        modify_gateway = False

        _, existing_node = self.get_node_by_id(node_id=node_id)
        if existing_node:
            try:
                GatewayType(existing_node.node_type)
            except ValueError:
                raise bpmn_exception.BpmnNodeTypeError("Node with given ID is not a gateway")
            else:
                modify_gateway = True

        gateway_id, gateway = self.add_modify_flow_node_to_diagram(
            process_id=process_id,
            node_type=gateway_type,
            name=gateway_name,
            node_id=node_id,
            modify=modify_gateway)

        if not isinstance(gateway, Gateway):
            raise bpmn_exception.BpmnNodeTypeError("Node with given ID is not a gateway")

        gateway.gateway_direction = gateway_direction
        if default_target_id:
            gateway.default_target_id = default_target_id

        # self.diagram_graph.nodes[gateway_id][consts.Consts.gateway_direction] = gateway_direction.value
        # if default_target_id:
        #     self.diagram_graph.nodes[gateway_id][consts.Consts.default] = default_target_id

        return gateway_id, gateway

    def add_modify_sequence_flow_to_diagram(self,
                                            process_id: str,
                                            source_ref_id: str,
                                            target_ref_id: str,
                                            sequence_flow_id: str = None,
                                            sequence_flow_name: str = "") -> tuple[str, SequenceFlow]:
        """
        Add or modify a SequenceFlow element to BPMN diagram. If sequence_flow_id matches existing sequence flow, it will be modified.

        Args:
            process_id (str): ID of parent process,
            source_ref_id (str): ID of source node,
            target_ref_id (str): ID of target node,
            sequence_flow_id (str): ID of sequence flow. Default value - None,
            sequence_flow_name (str): name of sequence flow. Default value - "".

        Returns:
            tuple: first value is sequence flow ID, second - a reference to created object.
        """
        if sequence_flow_id is None:
            sequence_flow_id = Consts.id_prefix + str(uuid.uuid4())

        existing_flow = self.get_flow_by_id(flow_id=sequence_flow_id)

        if existing_flow:
            self.delete_sequence_flow(sequence_flow_id=sequence_flow_id)

        new_flow = SequenceFlow(
            id=sequence_flow_id,
            name=sequence_flow_name,
            source_ref_id=source_ref_id,
            target_ref_id=target_ref_id,
            process_id=process_id,
        )
        source_node = self.nodes[source_ref_id]
        target_node = self.nodes[target_ref_id]

        new_flow.waypoints = [(source_node.x, source_node.y), (target_node.x, target_node.y)]

        self.sequence_flows[sequence_flow_id] = new_flow
        source_node.outgoing += [sequence_flow_id]
        target_node.incoming += [sequence_flow_id]

        # flow = self.diagram_graph[source_ref_id][target_ref_id]
        # flow[consts.Consts.id] = sequence_flow_id
        # flow[consts.Consts.name] = sequence_flow_name
        # flow[consts.Consts.process] = process_id
        # flow[consts.Consts.source_ref] = source_ref_id
        # flow[consts.Consts.target_ref] = target_ref_id
        # source_node = self.diagram_graph.nodes[source_ref_id]
        # target_node = self.diagram_graph.nodes[target_ref_id]

        # flow[consts.Consts.waypoints] = \
        #     [(source_node[consts.Consts.x], source_node[consts.Consts.y]),
        #      (target_node[consts.Consts.x], target_node[consts.Consts.y])]

        # add target node (target_ref_id) as outgoing node from source node (source_ref_id)
        # source_node[consts.Consts.outgoing_flow].append(sequence_flow_id)

        # add source node (source_ref_id) as incoming node to target node (target_ref_id)
        # target_node[consts.Consts.incoming_flow].append(sequence_flow_id)
        return sequence_flow_id, new_flow

    def delete_sequence_flow(self, sequence_flow_id: str) -> None:
        """
        Deletes a sequence flow from the diagram graph.

        Args:
            sequence_flow_id (str): ID of the sequence flow to be deleted
        """
        existing_flow = self.get_flow_by_id(flow_id=sequence_flow_id)
        if not existing_flow:
            raise bpmn_exception.BpmnFlowNotFoundError("Flow with given ID does not exist")

        source_node_id, target_node_id, flow = existing_flow
        source_node = self.nodes[source_node_id]
        target_node = self.nodes[target_node_id]

        self.sequence_flows.pop(sequence_flow_id)
        source_node.outgoing.remove(flow.id)
        target_node.incoming.remove(flow.id)

        # Remove the sequence flow from the nodes' incoming and outgoing flow lists
        # self.diagram_graph.remove_edge(source_node, target_node)
        # source_node[consts.Consts.outgoing_flow].remove(sequence_flow_id)
        # target_node[consts.Consts.incoming_flow].remove(sequence_flow_id)

    def delete_node(self, node_id: str, force_remove_sequence_flows: bool = False) -> None:
        """
        Deletes a node from the diagram graph.

        Args:
            node_id (str): ID of the node to be deleted
            force_remove_sequence_flows (bool): If True, all incoming and outgoing flows will be removed. Default value - False.
        """
        existing_node = self.get_node_by_id(node_id=node_id)
        if not existing_node:
            raise bpmn_exception.BpmnConnectedFlowsError("Node with given ID does not exist")

        _, node = existing_node
        if len(node.outgoing + node.incoming) > 0 and not force_remove_sequence_flows:
            raise bpmn_exception.BpmnPythonError(
                "Cannot delete node with incoming or outgoing flows, remove flows first or set force_remove_flows to True")

        flow_ids = node.incoming + node.outgoing
        for flow_id in flow_ids:
            self.delete_sequence_flow(flow_id)

        self.nodes.pop(node_id)

    def get_diagram_graph(self) -> nx.Graph:
        """
        Returns the diagram graph.

        Returns:
            nx.Graph: The diagram graph.
        """

        raise NotImplementedError()
        return nx.Graph()
