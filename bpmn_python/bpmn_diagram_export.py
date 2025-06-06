# coding=utf-8
"""
Package provides functionality for exporting graph representation to BPMN 2.0 XML
"""
import errno
import os
import xml.etree.cElementTree as eTree
from xml.etree.ElementTree import Element

from pydantic import BaseModel

import bpmn_python.bpmn_python_consts as consts
from bpmn_python.bpmn_diagram_rep import BpmnDiagramGraph
from bpmn_python.graph.classes.activities.subprocess import SubProcess
from bpmn_python.graph.classes.activities.task import Task
from bpmn_python.graph.classes.data_object import DataObject
from bpmn_python.graph.classes.events.boundary_event import BoundaryEvent
from bpmn_python.graph.classes.events.end_event import EndEvent
from bpmn_python.graph.classes.events.intermediate_catch_event import IntermediateCatchEvent
from bpmn_python.graph.classes.events.intermediate_throw_event import IntermediateThrowEvent
from bpmn_python.graph.classes.events.start_event import StartEvent
from bpmn_python.graph.classes.flow_node import FlowNode
from bpmn_python.graph.classes.gateways.complex_gateway import ComplexGateway
from bpmn_python.graph.classes.gateways.event_based_gateway import EventBasedGateway
from bpmn_python.graph.classes.gateways.exclusive_gateway import ExclusiveGateway
from bpmn_python.graph.classes.gateways.gateway import Gateway
from bpmn_python.graph.classes.gateways.inclusive_gateway import InclusiveGateway
from bpmn_python.graph.classes.gateways.parallel_gateway import ParallelGateway
from bpmn_python.graph.classes.lane_set import LaneSet, Lane
from bpmn_python.graph.classes.root_element.process import Process
from bpmn_python.graph.classes.sequence_flow import SequenceFlow


class BpmnDiagramGraphExport(BaseModel):
    """
    Class BPMNDiagramGraphExport provides methods for exporting BPMNDiagramGraph into BPMN 2.0 XML file.
    As a utility class, it only contains static methods.
    This class is meant to be used from BPMNDiagramGraph class.
    """

    @staticmethod
    def export_task_info(task: Task, output_element: Element):
        """
        Adds Task node attributes to exported XML element

        :param task: a Task object,
        :param output_element: object representing BPMN XML 'task' element.
        """
        if task.default is not None:
            output_element.set(consts.Consts.default, task.default)

    @staticmethod
    def export_subprocess_info(bpmn_diagram: BpmnDiagramGraph, subprocess: SubProcess, output_element: Element):
        """
        Adds Subprocess node attributes to exported XML element

        :param bpmn_diagram: BPMNDiagramGraph class instance representing a BPMN process diagram,
        :param subprocess: dictionary with given subprocess parameters,
        :param output_element: object representing BPMN XML 'subprocess' element.
        """
        output_element.set(consts.Consts.triggered_by_event, str(subprocess.triggered_by_event).lower())
        if subprocess.default is not None:
            output_element.set(consts.Consts.default, subprocess.default)

        # for each node in graph add correct type of element, its attributes and BPMNShape element
        subprocess_id = subprocess.id
        nodes = bpmn_diagram.get_nodes_list_by_process_id(subprocess_id)
        for node in nodes:
            node_id = node[0]
            params = node[1]
            BpmnDiagramGraphExport.export_node_data(bpmn_diagram, node_id, params, output_element)

        # for each edge in graph add sequence flow element, its attributes and BPMNEdge element
        flows = bpmn_diagram.get_flows_list_by_process_id(subprocess_id)
        for _, _, flow in flows:
            params = flow
            BpmnDiagramGraphExport.export_flow_process_data(params, output_element)

    @staticmethod
    def export_data_object_info(bpmn_diagram: BpmnDiagramGraph, data_object: DataObject, output_element: Element):
        """
        Adds DataObject node attributes to exported XML element

        :param bpmn_diagram: BPMNDiagramGraph class instance representing a BPMN process diagram,
        :param data_object: dictionary with given subprocess parameters,
        :param output_element: object representing BPMN XML 'subprocess' element.
        """
        output_element.set(consts.Consts.is_collection, str(data_object.is_collection).lower())

    # TODO Complex gateway not fully supported
    #  need to find out how sequence of conditions is represented in BPMN 2.0 XML
    @staticmethod
    def export_complex_gateway_info(gateway: ComplexGateway, output_element: Element):
        """
        Adds ComplexGateway node attributes to exported XML element

        :param gateway: complex gateway object,
        :param output_element: object representing BPMN XML 'complexGateway' element.
        """
        output_element.set(consts.Consts.gateway_direction, gateway.gateway_direction.value)
        # TODO complex_gateway_default
        # if gateway.default_target_id is not None:
        #     output_element.set(consts.Consts.default, gateway.default_target_id)

    @staticmethod
    def export_event_based_gateway_info(gateway: EventBasedGateway, output_element: Element):
        """
        Adds EventBasedGateway node attributes to exported XML element

        :param gateway: EventBasedGateway object,
        :param output_element: object representing BPMN XML 'eventBasedGateway' element.
        """
        output_element.set(consts.Consts.gateway_direction, gateway.gateway_direction.value)
        output_element.set(consts.Consts.instantiate, str(gateway.instantiate).lower())
        output_element.set(consts.Consts.event_gateway_type, gateway.event_gateway_type.value)

    @staticmethod
    def export_inclusive_exclusive_gateway_info(gateway: Gateway, output_element: Element):
        """
        Adds InclusiveGateway or ExclusiveGateway node attributes to exported XML element

        :param gateway: inclusive or exclusive gateway,
        :param output_element: object representing BPMN XML 'inclusiveGateway'/'exclusive' element.
        """
        if not isinstance(gateway, InclusiveGateway) and not isinstance(gateway, ExclusiveGateway):
            raise TypeError("Expected Gateway or ComplexGateway instance")

        output_element.set(consts.Consts.gateway_direction, gateway.gateway_direction.value)
        if gateway.default is not None:
            output_element.set(consts.Consts.default, gateway.default)

    @staticmethod
    def export_parallel_gateway_info(gateway: ParallelGateway, output_element: Element):
        """
        Adds parallel gateway node attributes to exported XML element

        :param gateway: parallel gateway,
        :param output_element: object representing BPMN XML 'parallelGateway' element.
        """
        output_element.set(consts.Consts.gateway_direction, gateway.gateway_direction.value)

    @staticmethod
    def export_catch_event_info(event: IntermediateCatchEvent, output_element: Element):
        """
        Adds IntermediateCatchEvent attributes to exported XML element

        :param event: intermediate catch event,
        :param output_element: object representing BPMN XML 'intermediateCatchEvent' element.
        """
        output_element.set(consts.Consts.parallel_multiple, str(event.parallel_multiple).lower())
        definitions = event.event_definition_list
        for definition in definitions:
            definition_id = definition.id
            definition_type = definition.definition_type
            output_definition = eTree.SubElement(output_element, definition_type.value)
            if definition_id != "":
                output_definition.set(consts.Consts.id, definition_id)

    @staticmethod
    def export_start_event_info(event: StartEvent, output_element: Element):
        """
        Adds StartEvent attributes to exported XML element

        :param event: intermediate catch event,
        :param output_element: object representing BPMN XML 'intermediateCatchEvent' element.
        """
        output_element.set(consts.Consts.parallel_multiple, str(event.parallel_multiple).lower())
        output_element.set(consts.Consts.is_interrupting, str(event.is_interrupting).lower())
        definitions = event.event_definition_list
        for definition in definitions:
            definition_id = definition.id
            definition_type = definition.definition_type.value
            output_definition = eTree.SubElement(output_element, definition_type)
            if definition_id != "":
                output_definition.set(consts.Consts.id, definition_id)

    @staticmethod
    def export_throw_event_info(event: IntermediateThrowEvent, output_element: Element):
        """
        Adds EndEvent or IntermediateThrowingEvent attributes to exported XML element

        :param event: intermediate throw event,
        :param output_element: object representing BPMN XML 'intermediateThrowEvent' element.
        """
        definitions = event.event_definition_list
        for definition in definitions:
            definition_id = definition.id
            definition_type = definition.definition_type
            output_definition = eTree.SubElement(output_element, definition_type.value)
            if definition_id != "":
                output_definition.set(consts.Consts.id, definition_id)

    @staticmethod
    def export_boundary_event_info(event: BoundaryEvent, output_element: Element):
        """
        Adds BoundaryEvent attributes to exported XML element

        :param event: dictionary with given intermediate catch event parameters,
        :param output_element: object representing BPMN XML 'boundaryEvent' element.
        """
        output_element.set(consts.Consts.parallel_multiple, str(event.parallel_multiple).lower())
        output_element.set(consts.Consts.cancel_activity, str(event.cancel_activity).lower())
        output_element.set(consts.Consts.attached_to_ref, event.attached_to_ref)
        definitions = event.event_definition_list
        for definition in definitions:
            definition_id = definition.id
            definition_type = definition.definition_type
            output_definition = eTree.SubElement(output_element, definition_type.value)
            if definition_id != "":
                output_definition.set(consts.Consts.id, definition_id)

    @staticmethod
    def export_definitions_element() -> Element:
        """
        Creates root element ('definitions') for exported BPMN XML file.

        :return: definitions XML element.
        """
        root = eTree.Element(consts.Consts.definitions)
        root.set("xmlns", "http://www.omg.org/spec/BPMN/20100524/MODEL")
        root.set("xmlns:bpmndi", "http://www.omg.org/spec/BPMN/20100524/DI")
        root.set("xmlns:omgdc", "http://www.omg.org/spec/DD/20100524/DC")
        root.set("xmlns:omgdi", "http://www.omg.org/spec/DD/20100524/DI")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.set("targetNamespace", "http://www.signavio.com/bpmn20")
        root.set("typeLanguage", "http://www.w3.org/2001/XMLSchema")
        root.set("expressionLanguage", "http://www.w3.org/1999/XPath")
        root.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")

        return root

    @staticmethod
    def export_process_element(definitions: Element, process_id: str, process: Process) -> Element:
        """
        Creates process element for exported BPMN XML file.

        :param definitions: an XML element ('definitions'), root element of BPMN 2.0 document
        :param process_id: string object. ID of exported process element,
        :param process: Process object containing process attributes.
        :return: process XML element
        """
        process_element = eTree.SubElement(definitions, consts.Consts.process)
        process_element.set(consts.Consts.id, process_id)
        process_element.set(consts.Consts.is_closed, str(process.is_closed).lower())
        process_element.set(consts.Consts.is_executable, str(process.is_executable).lower())
        process_element.set(consts.Consts.process_type, process.process_type.value)

        return process_element

    @staticmethod
    def export_lane_set(process_element, lane_set: LaneSet, plane_element: Element):
        """
        Creates 'laneSet' element for exported BPMN XML file.

        :param process_element: an XML element ('process'), from exported BPMN 2.0 document,
        :param lane_set: LaneSet object containing lane set attributes and child elements,
        :param plane_element: XML object, representing 'plane' element of exported BPMN 2.0 XML.
        """
        lane_set_xml = eTree.SubElement(process_element, consts.Consts.lane_set)
        for key, value in lane_set.lanes.items():
            BpmnDiagramGraphExport.export_lane(lane_set_xml, key, value, plane_element)

    @staticmethod
    def export_child_lane_set(parent_xml_element: Element, child_lane_set: LaneSet, plane_element: Element):
        """
        Creates 'childLaneSet' element for exported BPMN XML file.

        :param parent_xml_element: an XML element, parent of exported 'childLaneSet' element,
        :param child_lane_set: dictionary with exported 'childLaneSet' element attributes and child elements,
        :param plane_element: XML object, representing 'plane' element of exported BPMN 2.0 XML.
        """
        lane_set_xml = eTree.SubElement(parent_xml_element, consts.Consts.lane_set)
        for key, value in child_lane_set.lanes.items():
            BpmnDiagramGraphExport.export_lane(lane_set_xml, key, value, plane_element)

    @staticmethod
    def export_lane(parent_xml_element: Element, lane_id: str, lane: Lane, plane_element: Element):
        """
        Creates 'lane' element for exported BPMN XML file.

        :param parent_xml_element: an XML element, parent of exported 'lane' element,
        :param lane_id: string object. ID of exported lane element,
        :param lane: Lane object containing lane attributes,
        :param plane_element: XML object, representing 'plane' element of exported BPMN 2.0 XML.
        """
        lane_xml = eTree.SubElement(parent_xml_element, consts.Consts.lane)
        lane_xml.set(consts.Consts.id, lane_id)
        lane_xml.set(consts.Consts.name, lane.name)
        if lane.child_lane_set is not None and len(lane.child_lane_set.lanes) > 0:
            child_lane_set = lane.child_lane_set
            BpmnDiagramGraphExport.export_child_lane_set(lane_xml, child_lane_set, plane_element)
        if len(lane.flow_node_refs) > 0:
            for flow_node_ref_id in lane.flow_node_refs:
                flow_node_ref_xml = eTree.SubElement(lane_xml, consts.Consts.flow_node_ref)
                flow_node_ref_xml.text = flow_node_ref_id

        output_element_di = eTree.SubElement(plane_element, consts.Consts.bpmndi_namespace + consts.Consts.bpmn_shape)
        output_element_di.set(consts.Consts.id, lane_id + "_gui")

        output_element_di.set(consts.Consts.bpmn_element, lane_id)
        output_element_di.set(consts.Consts.is_horizontal, str(lane.is_horizontal).lower())
        bounds = eTree.SubElement(output_element_di, "omgdc:Bounds")
        bounds.set(consts.Consts.width, str(lane.width))
        bounds.set(consts.Consts.height, str(lane.height))
        bounds.set(consts.Consts.x, str(lane.x))
        bounds.set(consts.Consts.y, str(lane.y))

    @staticmethod
    def export_diagram_plane_elements(root: Element, diagram_attributes: dict[str, str],
                                      plane_attributes: dict[str, str]) -> tuple[Element, Element]:
        """
        Creates 'diagram' and 'plane' elements for exported BPMN XML file.
        Returns a tuple (diagram, plane).

        :param root: object of Element class, representing a BPMN XML root element ('definitions'),
        :param diagram_attributes: dictionary that holds attribute values for imported 'BPMNDiagram' element,
        :param plane_attributes: dictionary that holds attribute values for imported 'BPMNPlane' element.
        """
        diagram = eTree.SubElement(root, consts.Consts.bpmndi_namespace + "BPMNDiagram")
        diagram.set(consts.Consts.id, diagram_attributes[consts.Consts.id])
        diagram.set(consts.Consts.name, diagram_attributes[consts.Consts.name])

        plane = eTree.SubElement(diagram, consts.Consts.bpmndi_namespace + "BPMNPlane")
        plane.set(consts.Consts.id, plane_attributes[consts.Consts.id])
        plane.set(consts.Consts.bpmn_element, plane_attributes[consts.Consts.bpmn_element])

        return diagram, plane

    @staticmethod
    def export_node_data(bpmn_diagram: BpmnDiagramGraph, process_id: str, node: FlowNode, process: Element):
        """
        Creates a new XML element (depends on node type) for given node parameters and adds it to 'process' element.

        :param bpmn_diagram: BPMNDiagramGraph class instance representing a BPMN process diagram,
        :param process_id: string representing ID of given flow node,
        :param node: dictionary with node parameters,
        :param process: object of Element class, representing BPMN XML 'process' element (root for nodes).
        """
        node_type = node.node_type
        output_element = eTree.SubElement(process, node_type.value)
        output_element.set(consts.Consts.id, process_id)
        output_element.set(consts.Consts.name, node.name)

        for incoming in node.incoming:
            incoming_element = eTree.SubElement(output_element, consts.Consts.incoming_flow)
            incoming_element.text = incoming
        for outgoing in node.outgoing:
            outgoing_element = eTree.SubElement(output_element, consts.Consts.outgoing_flow)
            outgoing_element.text = outgoing

        if isinstance(node, Task):
            BpmnDiagramGraphExport.export_task_info(node, output_element)
        elif isinstance(node, SubProcess):
            BpmnDiagramGraphExport.export_subprocess_info(bpmn_diagram, node, output_element)
        elif isinstance(node, DataObject):
            BpmnDiagramGraphExport.export_data_object_info(bpmn_diagram, node, output_element)
        elif isinstance(node, ComplexGateway):
            BpmnDiagramGraphExport.export_complex_gateway_info(node, output_element)
        elif isinstance(node, EventBasedGateway):
            BpmnDiagramGraphExport.export_event_based_gateway_info(node, output_element)
        elif isinstance(node, InclusiveGateway) or isinstance(node, ExclusiveGateway):
            BpmnDiagramGraphExport.export_inclusive_exclusive_gateway_info(node, output_element)
        elif isinstance(node, ParallelGateway):
            BpmnDiagramGraphExport.export_parallel_gateway_info(node, output_element)
        elif isinstance(node, StartEvent):
            BpmnDiagramGraphExport.export_start_event_info(node, output_element)
        elif isinstance(node, IntermediateCatchEvent):
            BpmnDiagramGraphExport.export_catch_event_info(node, output_element)
        elif isinstance(node, EndEvent) or isinstance(node, IntermediateThrowEvent):
            BpmnDiagramGraphExport.export_throw_event_info(node, output_element)
        elif isinstance(node, BoundaryEvent):
            BpmnDiagramGraphExport.export_boundary_event_info(node, output_element)

    @staticmethod
    def export_node_di_data(node_id: str, node: FlowNode, plane: Element):
        """
        Creates a new BPMNShape XML element for given node parameters and adds it to 'plane' element.

        :param node_id: string representing ID of given flow node,
        :param node: FlowNode object containing node parameters,
        :param plane: object of Element class, representing BPMN XML 'BPMNPlane' element (root for node DI data).
        """
        output_element_di = eTree.SubElement(plane, consts.Consts.bpmndi_namespace + consts.Consts.bpmn_shape)
        output_element_di.set(consts.Consts.id, node_id + "_gui")

        output_element_di.set(consts.Consts.bpmn_element, node_id)
        bounds = eTree.SubElement(output_element_di, "omgdc:Bounds")
        bounds.set(consts.Consts.width, str(node.width))
        bounds.set(consts.Consts.height, str(node.height))
        bounds.set(consts.Consts.x, str(node.x))
        bounds.set(consts.Consts.y, str(node.y))
        if isinstance(node, SubProcess):
            output_element_di.set(consts.Consts.is_expanded, str(node.is_expanded).lower())

    @staticmethod
    def export_flow_process_data(flow: SequenceFlow, process: Element):
        """
        Creates a new SequenceFlow XML element for given edge parameters and adds it to 'process' element.

        :param flow: SequenceFlow object containing edge parameters,
        :param process: object of Element class, representing BPMN XML 'process' element (root for sequence flows)
        """
        output_flow = eTree.SubElement(process, consts.Consts.sequence_flow)
        output_flow.set(consts.Consts.id, flow.id)
        output_flow.set(consts.Consts.name, flow.name)
        output_flow.set(consts.Consts.source_ref, flow.source_ref_id)
        output_flow.set(consts.Consts.target_ref, flow.target_ref_id)
        if flow.condition_expression is not None:
            condition_expression_params = flow.condition_expression
            condition_expression = eTree.SubElement(output_flow, consts.Consts.condition_expression)
            condition_expression.set(consts.Consts.id, condition_expression_params.id)
            condition_expression.text = condition_expression_params.condition
            output_flow.set(consts.Consts.name, condition_expression_params.condition)

    @staticmethod
    def export_flow_di_data(flow: SequenceFlow, plane: Element):
        """
        Creates a new BPMNEdge XML element for given edge parameters and adds it to 'plane' element.

        :param flow: SequenceFlow object containing edge parameters,
        :param plane: object of Element class, representing BPMN XML 'BPMNPlane' element (root for edge DI data).
        """
        output_flow = eTree.SubElement(plane, consts.Consts.bpmndi_namespace + consts.Consts.bpmn_edge)
        output_flow.set(consts.Consts.id, flow.id + "_gui")
        output_flow.set(consts.Consts.bpmn_element, flow.id)
        waypoints = flow.waypoints
        for waypoint in waypoints:
            waypoint_element = eTree.SubElement(output_flow, "omgdi:waypoint")
            waypoint_element.set(consts.Consts.x, waypoint[0])
            waypoint_element.set(consts.Consts.y, waypoint[1])

    @staticmethod
    def export_xml_file(directory: str, filename: str, bpmn_diagram: BpmnDiagramGraph):
        """
        Exports diagram inner graph to BPMN 2.0 XML file (with Diagram Interchange data).

        :param directory: string representing output directory,
        :param filename: string representing output file name,
        :param bpmn_diagram: BPMNDiagramGraph class instance representing a BPMN process diagram.
        """
        diagram_attributes = bpmn_diagram.diagram_attributes
        plane_attributes = bpmn_diagram.plane_attributes
        message_flows = bpmn_diagram.message_flows
        participants = bpmn_diagram.participants
        process_elements_dict = bpmn_diagram.process_elements
        definitions = BpmnDiagramGraphExport.export_definitions_element()

        [_, plane] = BpmnDiagramGraphExport.export_diagram_plane_elements(definitions, diagram_attributes,
                                                                          plane_attributes)

        # Add collaboration
        collaboration_xml = eTree.SubElement(definitions, consts.Consts.collaboration)
        collaboration_xml.set(consts.Consts.id, bpmn_diagram.collaboration_id)

        for message_flow_id, message_flow in message_flows.items():
            message_flow_xml = eTree.SubElement(collaboration_xml, consts.Consts.message_flow)
            message_flow_xml.set(consts.Consts.id, message_flow_id)
            message_flow_xml.set(consts.Consts.name, message_flow.name)
            message_flow_xml.set(consts.Consts.source_ref, message_flow.source_ref)
            message_flow_xml.set(consts.Consts.target_ref, message_flow.target_ref)

            message_flow_params = bpmn_diagram.get_flow_by_id(message_flow_id)[2]
            output_flow = eTree.SubElement(plane, consts.Consts.bpmndi_namespace + consts.Consts.bpmn_edge)
            output_flow.set(consts.Consts.id, message_flow_id + "_gui")
            output_flow.set(consts.Consts.bpmn_element, message_flow_id)
            waypoints = message_flow_params.waypoints
            for waypoint in waypoints:
                waypoint_element = eTree.SubElement(output_flow, "omgdi:waypoint")
                waypoint_element.set(consts.Consts.x, waypoint[0])
                waypoint_element.set(consts.Consts.y, waypoint[1])

        for participant_id, participant in participants.items():
            participant_xml = eTree.SubElement(collaboration_xml, consts.Consts.participant)
            participant_xml.set(consts.Consts.id, participant_id)
            participant_xml.set(consts.Consts.name, participant.name)
            participant_xml.set(consts.Consts.process_ref, participant.process_ref)

            output_element_di = eTree.SubElement(plane, consts.Consts.bpmndi_namespace +
                                                 consts.Consts.bpmn_shape)
            output_element_di.set(consts.Consts.id, participant_id + "_gui")
            output_element_di.set(consts.Consts.bpmn_element, participant_id)
            output_element_di.set(consts.Consts.is_horizontal, str(participant.is_horizontal).lower())
            bounds = eTree.SubElement(output_element_di, "omgdc:Bounds")
            bounds.set(consts.Consts.width, str(participant.width))
            bounds.set(consts.Consts.height, str(participant.height))
            bounds.set(consts.Consts.x, str(participant.x))
            bounds.set(consts.Consts.y, str(participant.y))

        for process_id in process_elements_dict:
            process_element = process_elements_dict[process_id]
            process = BpmnDiagramGraphExport.export_process_element(definitions, process_id, process_element)
            if process_element.lane_set is not None:
                BpmnDiagramGraphExport.export_lane_set(process, process_element.lane_set, plane)

            # for each node in graph add correct type of element, its attributes and BPMNShape element
            nodes = bpmn_diagram.get_nodes_list_by_process_id(process_id)
            for node in nodes:
                node_id = node[0]
                params = node[1]
                BpmnDiagramGraphExport.export_node_data(bpmn_diagram, node_id, params, process)
                # BpmnDiagramGraphExport.export_node_di_data(node_id, params, plane)

            # for each edge in graph add sequence flow element, its attributes and BPMNEdge element
            flows = bpmn_diagram.get_flows_list_by_process_id(process_id)
            for flow in flows:
                params = flow[2]
                BpmnDiagramGraphExport.export_flow_process_data(params, process)
                # BpmnDiagramGraphExport.export_flow_di_data(params, plane)

        # Export DI data
        nodes = bpmn_diagram.get_nodes()
        for node in nodes:
            BpmnDiagramGraphExport.export_node_di_data(node.id, node, plane)

        flows = bpmn_diagram.get_flows()
        for flow in flows:
            params = flow[2]
            BpmnDiagramGraphExport.export_flow_di_data(params, plane)

        BpmnDiagramGraphExport.indent(definitions)
        tree = eTree.ElementTree(definitions)
        try:
            os.makedirs(directory)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        tree.write(directory + filename, encoding='utf-8', xml_declaration=True)

    @staticmethod
    def export_xml_file_no_di(directory: str, filename: str, bpmn_diagram: BpmnDiagramGraph):
        """
        Exports diagram inner graph to BPMN 2.0 XML file (without Diagram Interchange data).

        :param directory: string representing output directory,
        :param filename: string representing output file name,
        :param bpmn_diagram: BPMNDiagramGraph class instance representing a BPMN process diagram.
        """
        process_elements_dict = bpmn_diagram.process_elements
        definitions = BpmnDiagramGraphExport.export_definitions_element()

        for process_id in process_elements_dict:
            process_element_attr = process_elements_dict[process_id]
            process = BpmnDiagramGraphExport.export_process_element(definitions, process_id, process_element_attr)

            # for each node in graph add correct type of element, its attributes and BPMNShape element
            nodes = bpmn_diagram.nodes
            for node_id, node in nodes.items():
                BpmnDiagramGraphExport.export_node_data(bpmn_diagram, node_id, node, process)

            # for each edge in graph add sequence flow element, its attributes and BPMNEdge element
            flows = bpmn_diagram.sequence_flows  # TODO: message_flows ?
            for flow in flows.values():
                BpmnDiagramGraphExport.export_flow_process_data(flow, process)

        BpmnDiagramGraphExport.indent(definitions)
        tree = eTree.ElementTree(definitions)
        try:
            os.makedirs(directory)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        tree.write(directory + filename, encoding='utf-8', xml_declaration=True)

    # Helper methods
    @staticmethod
    def indent(elem: Element, level: int = 0) -> Element:
        """
        Helper function, adds indentation to XML output.

        :param elem: object of Element class, representing element to which method adds indentation,
        :param level: current level of indentation.
        """
        i = "\n" + level * "  "
        j = "\n" + (level - 1) * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for subelem in elem:
                BpmnDiagramGraphExport.indent(subelem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = j
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = j
        return elem
