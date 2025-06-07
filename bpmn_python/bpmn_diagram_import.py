# coding=utf-8
"""
Package provides functionality for importing from BPMN 2.0 XML to graph representation
"""
from xml.dom import minidom
from xml.dom.minidom import Element

from pydantic import BaseModel

import bpmn_python.bpmn_import_utils as utils
import bpmn_python.bpmn_python_consts as consts
from bpmn_python.bpmn_diagram_rep import BpmnDiagramGraph
from bpmn_python.bpmn_import_utils import BpmnImportUtils
from bpmn_python.graph.classes.activities.activity import Activity
from bpmn_python.graph.classes.activities.subprocess import SubProcess
from bpmn_python.graph.classes.condition_expression import ConditionExpression
from bpmn_python.graph.classes.data_object import DataObject
from bpmn_python.graph.classes.events.boundary_event import BoundaryEvent
from bpmn_python.graph.classes.events.catch_event import CatchEvent
from bpmn_python.graph.classes.events.end_event import EndEvent
from bpmn_python.graph.classes.events.intermediate_catch_event import IntermediateCatchEvent
from bpmn_python.graph.classes.events.intermediate_throw_event import IntermediateThrowEvent
from bpmn_python.graph.classes.events.start_event import StartEvent
from bpmn_python.graph.classes.gateways.event_based_gateway import EventBasedGateway, EventBasedGatewayType
from bpmn_python.graph.classes.gateways.exclusive_gateway import ExclusiveGateway
from bpmn_python.graph.classes.gateways.gateway import Gateway, GatewayDirection
from bpmn_python.graph.classes.lane_set import LaneSet, Lane
from bpmn_python.graph.classes.message_flow import MessageFlow
from bpmn_python.graph.classes.participant import Participant
from bpmn_python.graph.classes.root_element.event_definition import EventDefinition, EventDefinitionType, \
    StartEventDefinitionTypes, EndEventDefinitionTypes, IntermediateThrowEventDefinitionTypes, \
    IntermediateCatchEventDefinitionTypes, BoundaryEventDefinitionTypes
from bpmn_python.graph.classes.root_element.process import Process, ProcessType
from bpmn_python.graph.classes.sequence_flow import SequenceFlow
from bpmn_python.node_creator import create_node, parse_node_type


class BpmnDiagramGraphImport(BaseModel):
    """
    Class BPMNDiagramGraphImport provides methods for importing BPMN 2.0 XML file.
    As a utility class, it only contains static methods. This class is meant to be used from BPMNDiagramGraph class.
    """

    @staticmethod
    def load_diagram_from_xml(filepath: str, diagram_graph: BpmnDiagramGraph):
        """
        Reads an XML file from given filepath and maps it into inner representation of BPMN diagram.
        Returns an instance of BPMNDiagramGraph class.

        :param filepath: string with output filepath,
        :param diagram_graph: an instance of BpmnDiagramGraph class.
        """
        diagram_attributes = diagram_graph.diagram_attributes
        plane_attributes = diagram_graph.plane_attributes

        document = BpmnDiagramGraphImport.read_xml_file(filepath)
        # According to BPMN 2.0 XML Schema, there's only one 'BPMNDiagram' and 'BPMNPlane'
        diagram_element = document.getElementsByTagNameNS("*", "BPMNDiagram")[0]
        plane_element = diagram_element.getElementsByTagNameNS("*", "BPMNPlane")[0]
        BpmnDiagramGraphImport.import_diagram_and_plane_attributes(diagram_attributes, plane_attributes,
                                                                   diagram_element, plane_element)

        BpmnDiagramGraphImport.import_process_elements(document, diagram_graph, plane_element)

        collaboration_element_list = document.getElementsByTagNameNS("*", consts.Consts.collaboration)
        if collaboration_element_list is not None and len(collaboration_element_list) > 0:
            # Diagram has multiple pools and lanes
            collaboration_element = collaboration_element_list[0]
            BpmnDiagramGraphImport.import_collaboration_element(diagram_graph, collaboration_element)

        for element in utils.BpmnImportUtils.iterate_elements(plane_element):
            if element.nodeType != element.TEXT_NODE:
                tag_name = utils.BpmnImportUtils.remove_namespace_from_tag_name(element.tagName)
                if tag_name == consts.Consts.bpmn_shape:
                    BpmnDiagramGraphImport.import_shape_di(diagram_graph, element)
                elif tag_name == consts.Consts.bpmn_edge:
                    BpmnDiagramGraphImport.import_flow_di(diagram_graph, element)

    @staticmethod
    def import_collaboration_element(diagram_graph: BpmnDiagramGraph, collaboration_element: Element):
        """
        Method that imports information from 'collaboration' element.

        :param diagram_graph: NetworkX graph representing a BPMN process diagram,
        :param collaboration_element: XML document element,
        """
        diagram_graph.collaboration_id = collaboration_element.getAttribute(consts.Consts.id)

        for element in utils.BpmnImportUtils.iterate_elements(collaboration_element):
            if element.nodeType != element.TEXT_NODE:
                tag_name = utils.BpmnImportUtils.remove_namespace_from_tag_name(element.tagName)
                if tag_name == consts.Consts.participant:
                    BpmnDiagramGraphImport.import_participant_element(diagram_graph, element)
                elif tag_name == consts.Consts.message_flow:
                    BpmnDiagramGraphImport.import_message_flow_to_graph(diagram_graph, element)

    @staticmethod
    def import_participant_element(bpmn_diagram: BpmnDiagramGraph, participant_element: Element):
        """
        Adds 'participant' element to the collaboration dictionary.

        :param bpmn_diagram: BpmnDiagramGraph instance representing the BPMN diagram,
        :param participant_element: object representing a BPMN XML 'participant' element.
        """
        participants = bpmn_diagram.participants

        participant_id = participant_element.getAttribute(consts.Consts.id)
        name = participant_element.getAttribute(consts.Consts.name)
        process_ref = participant_element.getAttribute(consts.Consts.process_ref)

        # if participant_element.getAttribute(consts.Consts.process_ref) == '':
        #     diagram_graph.add_node(participant_id)
        #     diagram_graph.nodes[participant_id][consts.Consts.type] = consts.Consts.participant
        #     diagram_graph.nodes[participant_id][consts.Consts.process] = participant_id
        participants[participant_id] = Participant(id=participant_id, name=name, process_ref=process_ref)

    @staticmethod
    def import_diagram_and_plane_attributes(diagram_attributes: dict[str, str], plane_attributes: dict[str, str],
                                            diagram_element: Element, plane_element: Element):
        """
        Adds attributes of BPMN diagram and plane elements to appropriate
        fields diagram_attributes and plane_attributes.
        Diagram inner representation contains following diagram element attributes:

        - id - assumed to be required in XML file, even thought BPMN 2.0 schema doesn't say so,
        - name - optional parameter, empty string by default,
        
        Diagram inner representation contains following plane element attributes:

        - id - assumed to be required in XML file, even thought BPMN 2.0 schema doesn't say so,
        - bpmnElement - assumed to be required in XML file, even thought BPMN 2.0 schema doesn't say so,

        :param diagram_attributes: dictionary that holds attribute values for imported 'BPMNDiagram' element,
        :param plane_attributes: dictionary that holds attribute values for imported 'BPMNPlane' element,
        :param diagram_element: object representing a BPMN XML 'diagram' element,
        :param plane_element: object representing a BPMN XML 'plane' element.
        """
        diagram_attributes[consts.Consts.id] = diagram_element.getAttribute(consts.Consts.id)
        diagram_attributes[consts.Consts.name] = diagram_element.getAttribute(consts.Consts.name) \
            if diagram_element.hasAttribute(consts.Consts.name) else ""

        plane_attributes[consts.Consts.id] = plane_element.getAttribute(consts.Consts.id)
        plane_attributes[consts.Consts.bpmn_element] = plane_element.getAttribute(consts.Consts.bpmn_element)

    @staticmethod
    def import_process_elements(document: minidom.Document, diagram_graph: BpmnDiagramGraph, plane_element: Element):
        """
        Method for importing all 'process' elements in diagram.

        :param document: XML document,
        :param diagram_graph: NetworkX graph representing a BPMN process diagram,
        :param plane_element: object representing a BPMN XML 'plane' element.
        """
        processes = diagram_graph.process_elements
        for process_element in document.getElementsByTagNameNS("*", consts.Consts.process):
            BpmnDiagramGraphImport.import_process_element(processes, process_element)

            process_id = process_element.getAttribute(consts.Consts.id)
            process = processes[process_id]

            lane_set_list = process_element.getElementsByTagNameNS("*", consts.Consts.lane_set)
            if lane_set_list is not None and len(lane_set_list) > 0:
                # according to BPMN 2.0 XML Schema, there's at most one 'laneSet' element inside 'process'
                lane_set = lane_set_list[0]
                BpmnDiagramGraphImport.import_lane_set_element(process, lane_set, plane_element)

            for element in utils.BpmnImportUtils.iterate_elements(process_element):
                if element.nodeType != element.TEXT_NODE:
                    tag_name = utils.BpmnImportUtils.remove_namespace_from_tag_name(element.tagName)
                    BpmnDiagramGraphImport.__import_element_by_tag_name(diagram_graph, process_id, element, tag_name)

            for flow in utils.BpmnImportUtils.iterate_elements(process_element):
                if flow.nodeType != flow.TEXT_NODE:
                    tag_name = utils.BpmnImportUtils.remove_namespace_from_tag_name(flow.tagName)
                    if tag_name == consts.Consts.sequence_flow:
                        BpmnDiagramGraphImport.import_sequence_flow_to_graph(diagram_graph, process_id, flow)

    @staticmethod
    def __import_element_by_tag_name(diagram_graph: BpmnDiagramGraph, process_id: str, element: Element, tag_name: str):
        """
        Imports a BPMN element into the graph based on its tag name.

        :param diagram_graph: BpmnDiagramGraph instance representing the BPMN diagram,
        :param process_id: ID of the process the element belongs to.
        :param element: XML element representing the BPMN element.
        :param tag_name: Tag name of the BPMN element.
        """

        if tag_name == consts.Consts.task \
                or tag_name == consts.Consts.user_task \
                or tag_name == consts.Consts.service_task \
                or tag_name == consts.Consts.manual_task:
            BpmnDiagramGraphImport.import_task_to_graph(diagram_graph, process_id, element)
        elif tag_name == consts.Consts.subprocess:
            BpmnDiagramGraphImport.import_subprocess_to_graph(diagram_graph, process_id, element)
        elif tag_name == consts.Consts.data_object:
            BpmnDiagramGraphImport.import_data_object_to_graph(diagram_graph, process_id, element)
        elif tag_name == consts.Consts.inclusive_gateway or tag_name == consts.Consts.exclusive_gateway:
            BpmnDiagramGraphImport.import_incl_or_excl_gateway_to_graph(diagram_graph, process_id, element)
        elif tag_name == consts.Consts.parallel_gateway:
            BpmnDiagramGraphImport.import_parallel_gateway_to_graph(diagram_graph, process_id, element)
        elif tag_name == consts.Consts.event_based_gateway:
            BpmnDiagramGraphImport.import_event_based_gateway_to_graph(diagram_graph, process_id, element)
        elif tag_name == consts.Consts.complex_gateway:
            BpmnDiagramGraphImport.import_complex_gateway_to_graph(diagram_graph, process_id, element)
        elif tag_name == consts.Consts.start_event:
            BpmnDiagramGraphImport.import_start_event_to_graph(diagram_graph, process_id, element)
        elif tag_name == consts.Consts.end_event:
            BpmnDiagramGraphImport.import_end_event_to_graph(diagram_graph, process_id, element)
        elif tag_name == consts.Consts.intermediate_catch_event:
            BpmnDiagramGraphImport.import_intermediate_catch_event_to_graph(diagram_graph, process_id, element)
        elif tag_name == consts.Consts.intermediate_throw_event:
            BpmnDiagramGraphImport.import_intermediate_throw_event_to_graph(diagram_graph, process_id, element)
        elif tag_name == consts.Consts.boundary_event:
            BpmnDiagramGraphImport.import_boundary_event_to_graph(diagram_graph, process_id, element)

    @staticmethod
    def import_lane_set_element(process: Process, lane_set_element: Element, plane_element: Element):
        """
        Method for importing 'laneSet' element from diagram file.

        :param process: dictionary that holds attribute values of 'process' element, which is parent of
            imported flow node,
        :param lane_set_element: XML document element,
        :param plane_element: object representing a BPMN XML 'plane' element.
        """
        lane_set_id = lane_set_element.getAttribute(consts.Consts.id)
        lanes_dict = {}
        for element in utils.BpmnImportUtils.iterate_elements(lane_set_element):
            if element.nodeType != element.TEXT_NODE:
                tag_name = utils.BpmnImportUtils.remove_namespace_from_tag_name(element.tagName)
                if tag_name == consts.Consts.lane:
                    lane_element = element
                    lane_id = lane_element.getAttribute(consts.Consts.id)
                    lane = BpmnDiagramGraphImport.import_lane_element(lane_element, plane_element)
                    lanes_dict[lane_id] = lane

        lane_set = LaneSet(id=lane_set_id, lanes=lanes_dict)
        process.lane_set = lane_set

    @staticmethod
    def import_child_lane_set_element(child_lane_set_element, plane_element) -> LaneSet:
        """
        Method for importing 'childLaneSet' element from diagram file.

        :param child_lane_set_element: XML document element,
        :param plane_element: object representing a BPMN XML 'plane' element.
        """
        lane_set_id = child_lane_set_element.getAttribute(consts.Consts.id)
        lanes: dict[str, Lane] = {}
        for element in utils.BpmnImportUtils.iterate_elements(child_lane_set_element):
            if element.nodeType != element.TEXT_NODE:
                tag_name = utils.BpmnImportUtils.remove_namespace_from_tag_name(element.tagName)
                if tag_name == consts.Consts.lane:
                    lane_element = element
                    lane_id = lane_element.getAttribute(consts.Consts.id)
                    lane = BpmnDiagramGraphImport.import_lane_element(lane_element, plane_element)
                    lanes[lane_id] = lane

        child_lane_set_attr = LaneSet(id=lane_set_id, lanes=lanes)
        return child_lane_set_attr

    @staticmethod
    def import_lane_element(lane_element, plane_element) -> Lane:
        """
        Method for importing 'lane' element from diagram file.

        :param lane_element: XML document element,
        :param plane_element: object representing a BPMN XML 'plane' element.
        """

        lane_id = lane_element.getAttribute(consts.Consts.id)
        lane_name = lane_element.getAttribute(consts.Consts.name)
        child_lane_set: LaneSet | None = None
        flow_node_refs = []
        for element in utils.BpmnImportUtils.iterate_elements(lane_element):
            if element.nodeType != element.TEXT_NODE:
                tag_name = utils.BpmnImportUtils.remove_namespace_from_tag_name(element.tagName)
                if tag_name == consts.Consts.child_lane_set:
                    child_lane_set = BpmnDiagramGraphImport.import_child_lane_set_element(element, plane_element)
                elif tag_name == consts.Consts.flow_node_ref:
                    flow_node_ref_id = element.firstChild.nodeValue
                    flow_node_refs.append(flow_node_ref_id)

        lane = Lane(id=lane_id, name=lane_name, child_lane_set=child_lane_set, flow_node_refs=flow_node_refs)

        shape_element = None
        for element in utils.BpmnImportUtils.iterate_elements(plane_element):
            if element.nodeType != element.TEXT_NODE and element.getAttribute(consts.Consts.bpmn_element) == lane_id:
                shape_element = element
        if shape_element is not None:
            bounds = shape_element.getElementsByTagNameNS("*", "Bounds")[0]
            lane.is_horizontal = BpmnImportUtils.convert_str_to_bool(
                shape_element.getAttribute(consts.Consts.is_horizontal)
            )
            lane.width = BpmnImportUtils.convert_str_to_float(bounds.getAttribute(consts.Consts.width))
            lane.height = BpmnImportUtils.convert_str_to_float(bounds.getAttribute(consts.Consts.height))
            lane.x = BpmnImportUtils.convert_str_to_float(bounds.getAttribute(consts.Consts.x))
            lane.y = BpmnImportUtils.convert_str_to_float(bounds.getAttribute(consts.Consts.y))
        return lane

    @staticmethod
    def import_process_element(process_elements_dict: dict[str, Process], process_element: Element):
        """
        Adds attributes of BPMN process element to appropriate field process_attributes.
        Diagram inner representation contains following process attributes:

        - id - assumed to be required in XML file, even thought BPMN 2.0 schema doesn't say so,
        - isClosed - optional parameter, default value 'false',
        - isExecutable - optional parameter, default value 'false',
        - processType - optional parameter, default value 'None',
        - node_ids - list of flow nodes IDs, associated with given process.

        :param process_elements_dict: dictionary that holds attribute values for imported 'process' element. Key is
           process ID, value is a Process object,
        :param process_element: object representing a BPMN XML 'process' element.
        """
        process_id = process_element.getAttribute(consts.Consts.id)
        name = process_element.getAttribute(consts.Consts.name) \
            if process_element.hasAttribute(consts.Consts.name) else ""
        is_closed = BpmnImportUtils.convert_str_to_bool(
            process_element.getAttribute(consts.Consts.is_closed) \
                if process_element.hasAttribute(consts.Consts.is_closed) else "false"
        )
        is_executable = BpmnImportUtils.convert_str_to_bool(
            process_element.getAttribute(consts.Consts.is_executable) \
                if process_element.hasAttribute(consts.Consts.is_executable) else "false"
        )
        process_type = ProcessType.parse(
            process_element.getAttribute(consts.Consts.process_type) \
                if process_element.hasAttribute(consts.Consts.process_type) else "None"
        )

        process = Process(id=process_id, name=name, is_closed=is_closed, is_executable=is_executable,
                          process_type=process_type)
        process_elements_dict[process_id] = process

    @staticmethod
    def import_flow_node_to_graph(bpmn_diagram: BpmnDiagramGraph, process_id: str, flow_node_element: Element):
        """
        Adds a new node to graph.
        Input parameter is object of class xml.dom.Element.
        Nodes are identified by ID attribute of Element.
        Method adds basic attributes (shared by all BPMN elements) to node. Those elements are:

        - id - added as key value, we assume that this is a required value,
        - type - tagName of element, used to identify type of BPMN diagram element,
        - name - optional attribute, empty string by default.

        :param bpmn_diagram: BpmnDiagramGraph instance representing the BPMN diagram,
        :param process_id: string object, representing an ID of process element,
        :param flow_node_element: object representing a BPMN XML element corresponding to given flownode,
        """
        element_id = flow_node_element.getAttribute(consts.Consts.id)
        node_type = utils.BpmnImportUtils.remove_namespace_from_tag_name(flow_node_element.tagName)
        node = create_node(node_type=parse_node_type(node_type), node_id=element_id, process_id=process_id)
        node.name = flow_node_element.getAttribute(consts.Consts.name) \
            if flow_node_element.hasAttribute(consts.Consts.name) \
            else ""
        process = bpmn_diagram.process_elements[process_id]
        process.flow_element_list.append(node)

        # add incoming flow node list
        incoming_list = []
        for tmp_element in utils.BpmnImportUtils.iterate_elements(flow_node_element):
            if tmp_element.nodeType != tmp_element.TEXT_NODE:
                tag_name = utils.BpmnImportUtils.remove_namespace_from_tag_name(tmp_element.tagName)
                if tag_name == consts.Consts.incoming_flow:
                    incoming_value = tmp_element.firstChild.nodeValue
                    incoming_list.append(incoming_value)
        node.incoming = incoming_list

        # add outgoing flow node list
        outgoing_list = []
        for tmp_element in utils.BpmnImportUtils.iterate_elements(flow_node_element):
            if tmp_element.nodeType != tmp_element.TEXT_NODE:
                tag_name = utils.BpmnImportUtils.remove_namespace_from_tag_name(tmp_element.tagName)
                if tag_name == consts.Consts.outgoing_flow:
                    outgoing_value = tmp_element.firstChild.nodeValue
                    outgoing_list.append(outgoing_value)
        node.outgoing = outgoing_list

        bpmn_diagram.nodes[element_id] = node

    @staticmethod
    def import_task_to_graph(diagram_graph: BpmnDiagramGraph, process_id: str, task_element: Element):
        """
        Adds to graph the new element that represents BPMN task.
        In our representation tasks have only basic attributes and elements, inherited from Activity type,
        so this method only needs to call add_flownode_to_graph.

        :param diagram_graph: BpmnDiagramGraph instance representing the BPMN diagram,
        :param process_id: string object, representing an ID of process element,
        :param task_element: object representing a BPMN XML 'task' element.
        """
        BpmnDiagramGraphImport.import_activity_to_graph(diagram_graph, process_id, task_element)

    @staticmethod
    def import_subprocess_to_graph(diagram_graph: BpmnDiagramGraph, process_id: str, subprocess_element: Element):
        """
        Adds to graph the new element that represents BPMN subprocess.
        In addition to attributes inherited from FlowNode type, SubProcess
        has additional attribute triggeredByEvent (boolean type, default value - false).

        :param diagram_graph: BpmnDiagramGraph instance representing the BPMN diagram,
        :param process_id: string object, representing an ID of process element,
        :param subprocess_element: object representing a BPMN XML 'subprocess' element
        """

        BpmnDiagramGraphImport.import_activity_to_graph(diagram_graph, process_id,
                                                        subprocess_element)

        subprocess_id = subprocess_element.getAttribute(consts.Consts.id)
        triggered_by_event = BpmnImportUtils.convert_str_to_bool(
            subprocess_element.getAttribute(consts.Consts.triggered_by_event) \
                if subprocess_element.hasAttribute(consts.Consts.triggered_by_event) else "false")

        subprocess = SubProcess(id=subprocess_id, triggered_by_event=triggered_by_event)
        diagram_graph.nodes[subprocess_id] = subprocess

        for element in utils.BpmnImportUtils.iterate_elements(subprocess_element):
            if element.nodeType != element.TEXT_NODE:
                tag_name = utils.BpmnImportUtils.remove_namespace_from_tag_name(element.tagName)
                BpmnDiagramGraphImport.__import_element_by_tag_name(diagram_graph, subprocess_id, element, tag_name)

        for flow in utils.BpmnImportUtils.iterate_elements(subprocess_element):
            if flow.nodeType != flow.TEXT_NODE:
                tag_name = utils.BpmnImportUtils.remove_namespace_from_tag_name(flow.tagName)
                if tag_name == consts.Consts.sequence_flow:
                    BpmnDiagramGraphImport.import_sequence_flow_to_graph(diagram_graph, subprocess_id, flow)

    @staticmethod
    def import_data_object_to_graph(diagram_graph: BpmnDiagramGraph, process_id: str, data_object_element: Element):
        """
        Adds to graph the new element that represents BPMN data object.
        Data object inherits attributes from FlowNode. In addition, an attribute 'isCollection' is added to the node.

        :param diagram_graph: BpmnDiagramGraph instance representing the BPMN diagram,
        :param process_id: string object, representing an ID of process element,
        :param data_object_element: object representing a BPMN XML 'dataObject' element.
        """
        BpmnDiagramGraphImport.import_flow_node_to_graph(diagram_graph, process_id, data_object_element)
        data_object_id = data_object_element.getAttribute(consts.Consts.id)

        node = diagram_graph.nodes[data_object_id]
        if isinstance(node, DataObject):
            node.is_collection = BpmnImportUtils.convert_str_to_bool(
                data_object_element.getAttribute(consts.Consts.is_collection) \
                    if data_object_element.hasAttribute(consts.Consts.is_collection) else "false"
            )

    @staticmethod
    def import_activity_to_graph(diagram_graph: BpmnDiagramGraph, process_id: str, element: Element):
        """
        Method that adds the new element that represents BPMN activity.
        Should not be used directly, only as a part of method, that imports an element which extends Activity element
        (task, subprocess etc.)

        :param diagram_graph: BpmnDiagramGraph instance representing the BPMN diagram,
        :param process_id: string object, representing an ID of process element,
        :param element: object representing a BPMN XML element which extends 'activity'.
        """
        BpmnDiagramGraphImport.import_flow_node_to_graph(diagram_graph, process_id, element)

        element_id = element.getAttribute(consts.Consts.id)
        node = diagram_graph.nodes[element_id]
        if isinstance(node, Activity):
            node.default = element.getAttribute(consts.Consts.default) \
                if element.hasAttribute(consts.Consts.default) else None

    @staticmethod
    def import_gateway_to_graph(diagram_graph: BpmnDiagramGraph, process_id: str, element: Element):
        """
        Adds to graph the new element that represents BPMN gateway.
        In addition to attributes inherited from FlowNode type, Gateway
        has additional attribute gatewayDirection (simple type, default value - Unspecified).

        :param diagram_graph: BpmnDiagramGraph instance representing the BPMN diagram,
        :param process_id: string object, representing an ID of process element,
        :param element: object representing a BPMN XML element of Gateway type extension.
        """
        element_id = element.getAttribute(consts.Consts.id)
        BpmnDiagramGraphImport.import_flow_node_to_graph(diagram_graph, process_id, element)

        node = diagram_graph.nodes[element_id]
        if isinstance(node, Gateway):
            node.gateway_direction = GatewayDirection.parse(
                element.getAttribute(consts.Consts.gateway_direction) \
                    if element.hasAttribute(consts.Consts.gateway_direction) else "Unspecified"
            )

    @staticmethod
    def import_complex_gateway_to_graph(diagram_graph: BpmnDiagramGraph, process_id: str, element: Element):
        """
        Adds to graph the new element that represents BPMN complex gateway.
        In addition to attributes inherited from Gateway type, complex gateway
        has additional attribute default flow (default value - none).

        :param diagram_graph: BpmnDiagramGraph instance representing the BPMN diagram,
        :param process_id: string object, representing an ID of process element,
        :param element: object representing a BPMN XML 'complexGateway' element.
        """
        element_id = element.getAttribute(consts.Consts.id)
        BpmnDiagramGraphImport.import_gateway_to_graph(diagram_graph, process_id, element)

        # TODO sequence of conditions
        # Can't get any working example of Complex gateway, so I'm not sure how exactly those conditions are kept

    @staticmethod
    def import_event_based_gateway_to_graph(diagram_graph: BpmnDiagramGraph, process_id: str, element: Element):
        """
        Adds to graph the new element that represents BPMN event based gateway.
        In addition to attributes inherited from Gateway type, event based gateway has additional
        attributes - instantiate (boolean type, default value - false) and eventGatewayType
        (custom type tEventBasedGatewayType, default value - Exclusive).

        :param diagram_graph: BpmnDiagramGraph instance representing the BPMN diagram,
        :param process_id: string object, representing an ID of process element,
        :param element: object representing a BPMN XML 'eventBasedGateway' element.
        """
        element_id = element.getAttribute(consts.Consts.id)
        BpmnDiagramGraphImport.import_gateway_to_graph(diagram_graph, process_id, element)

        node = diagram_graph.nodes[element_id]
        if isinstance(node, EventBasedGateway):
            node.instantiate = BpmnImportUtils.convert_str_to_bool(
                element.getAttribute(consts.Consts.instantiate) \
                    if element.hasAttribute(consts.Consts.instantiate) else "false"
            )
            node.event_gateway_type = EventBasedGatewayType.parse(
                element.getAttribute(consts.Consts.event_gateway_type) \
                    if element.hasAttribute(consts.Consts.event_gateway_type) else "Exclusive"
            )

    @staticmethod
    def import_incl_or_excl_gateway_to_graph(diagram_graph: BpmnDiagramGraph, process_id: str, element: Element):
        """
        Adds to graph the new element that represents BPMN inclusive or exclusive gateway.
        In addition to attributes inherited from Gateway type, inclusive and exclusive gateway have additional
        attribute default flow (default value - none).

        :param diagram_graph: BpmnDiagramGraph instance representing the BPMN diagram,
        :param process_id: string object, representing an ID of process element,
        :param element: object representing a BPMN XML 'inclusiveGateway' or 'exclusiveGateway' element.
        """
        element_id = element.getAttribute(consts.Consts.id)
        BpmnDiagramGraphImport.import_gateway_to_graph(diagram_graph, process_id, element)

        node = diagram_graph.nodes[element_id]
        if isinstance(node, ExclusiveGateway):
            node.default = element.getAttribute(consts.Consts.default) \
                if element.hasAttribute(consts.Consts.default) else None

    @staticmethod
    def import_parallel_gateway_to_graph(diagram_graph: BpmnDiagramGraph, process_id: str, element: Element):
        """
        Adds to graph the new element that represents BPMN parallel gateway.
        Parallel gateway doesn't have additional attributes. Separate method is used to improve code readability.

        :param diagram_graph: BpmnDiagramGraph instance representing the BPMN diagram,
        :param process_id: string object, representing an ID of process element,
        :param element: object representing a BPMN XML 'parallelGateway'.
        """
        BpmnDiagramGraphImport.import_gateway_to_graph(diagram_graph, process_id, element)

    @staticmethod
    def import_event_definition_elements(diagram_graph: BpmnDiagramGraph, element: Element,
                                         event_definitions: set[EventDefinitionType]):
        """
        Helper function, that adds event definition elements (defines special types of events) to corresponding events.

        :param diagram_graph: BpmnDiagramGraph instance representing the BPMN diagram,
        :param element: object representing a BPMN XML event element,
        :param event_definitions: list of event definitions, that belongs to given event.
        """
        element_id = element.getAttribute(consts.Consts.id)
        event_def_list = []
        for definition_type in event_definitions:
            event_def_xml = element.getElementsByTagNameNS("*", definition_type.name)
            for index in range(len(event_def_xml)):
                event_def_tmp = EventDefinition(id=event_def_xml[index].getAttribute(consts.Consts.id),
                                                definition_type=definition_type)
                event_def_list.append(event_def_tmp)

        node = diagram_graph.nodes[element_id]
        if isinstance(node, StartEvent):
            node.event_definition_list = event_def_list
        elif isinstance(node, EndEvent):
            node.event_definition_list = event_def_list
        elif isinstance(node, IntermediateCatchEvent):
            node.event_definition_list = event_def_list
        elif isinstance(node, IntermediateThrowEvent):
            node.event_definition_list = event_def_list

    @staticmethod
    def import_start_event_to_graph(diagram_graph: BpmnDiagramGraph, process_id: str, element: Element):
        """
        Adds to graph the new element that represents BPMN start event.
        Start event inherits attribute parallelMultiple from CatchEvent type
        and sequence of eventDefinitionRef from Event type.
        Separate methods for each event type are required since each of them has different variants
        (Message, Error, Signal etc.).

        :param diagram_graph: a BpmnDiagramGraph object - a BPMN process diagram representation class,
        :param process_id: string object, representing an ID of process element,
        :param element: object representing a BPMN XML 'startEvent' element.
        """
        element_id = element.getAttribute(consts.Consts.id)
        start_event_definitions = StartEventDefinitionTypes.getTypes()
        BpmnDiagramGraphImport.import_flow_node_to_graph(diagram_graph, process_id, element)

        node = diagram_graph.nodes[element_id]
        if isinstance(node, StartEvent):
            node.parallel_multiple = BpmnImportUtils.convert_str_to_bool(
                element.getAttribute(consts.Consts.parallel_multiple) \
                    if element.hasAttribute(consts.Consts.parallel_multiple) else "false"
            )

            node.is_interrupting = BpmnImportUtils.convert_str_to_bool(
                element.getAttribute(consts.Consts.is_interrupting) \
                    if element.hasAttribute(consts.Consts.is_interrupting) else "true"
            )

        BpmnDiagramGraphImport.import_event_definition_elements(diagram_graph, element, start_event_definitions)

    @staticmethod
    def import_intermediate_catch_event_to_graph(diagram_graph: BpmnDiagramGraph, process_id: str, element: Element):
        """
        Adds to graph the new element that represents BPMN intermediate catch event.
        Intermediate catch event inherits attribute parallelMultiple from CatchEvent type
        and sequence of eventDefinitionRef from Event type.
        Separate methods for each event type are required since each of them has different variants
        (Message, Error, Signal etc.).

        :param diagram_graph: a BpmnDiagramGraph object - a BPMN process diagram representation class,
        :param process_id: string object, representing an ID of process element,
        :param element: object representing a BPMN XML 'intermediateCatchEvent' element.
        """
        element_id = element.getAttribute(consts.Consts.id)
        intermediate_catch_event_definitions = IntermediateCatchEventDefinitionTypes.getTypes()
        BpmnDiagramGraphImport.import_flow_node_to_graph(diagram_graph, process_id, element)

        node = diagram_graph.nodes[element_id]
        if isinstance(node, CatchEvent):
            node.parallel_multiple = BpmnImportUtils.convert_str_to_bool(
                element.getAttribute(consts.Consts.parallel_multiple) \
                    if element.hasAttribute(consts.Consts.parallel_multiple) else "false"
            )

        BpmnDiagramGraphImport.import_event_definition_elements(diagram_graph, element,
                                                                intermediate_catch_event_definitions)

    @staticmethod
    def import_end_event_to_graph(diagram_graph: BpmnDiagramGraph, process_id: str, element: Element):
        """
        Adds to graph the new element that represents BPMN end event.
        End event inherits sequence of eventDefinitionRef from Event type.
        Separate methods for each event type are required since each of them has different variants
        (Message, Error, Signal etc.).

        :param diagram_graph: a BpmnDiagramGraph object - a BPMN process diagram representation class,
        :param process_id: string object, representing an ID of process element,
        :param element: object representing a BPMN XML 'endEvent' element.
        """
        end_event_definitions = EndEventDefinitionTypes.getTypes()
        BpmnDiagramGraphImport.import_flow_node_to_graph(diagram_graph, process_id, element)
        BpmnDiagramGraphImport.import_event_definition_elements(diagram_graph, element, end_event_definitions)

    @staticmethod
    def import_intermediate_throw_event_to_graph(diagram_graph: BpmnDiagramGraph, process_id: str, element: Element):
        """
        Adds to graph the new element that represents BPMN intermediate throw event.
        Intermediate throw event inherits sequence of eventDefinitionRef from Event type.
        Separate methods for each event type are required since each of them has different variants
        (Message, Error, Signal etc.).

        :param diagram_graph: a BpmnDiagramGraph object - a BPMN process diagram representation class,
        :param process_id: string object, representing an ID of process element,
        :param element: object representing a BPMN XML 'intermediateThrowEvent' element.
        """
        intermediate_throw_event_definitions = IntermediateThrowEventDefinitionTypes.getTypes()
        BpmnDiagramGraphImport.import_flow_node_to_graph(diagram_graph, process_id, element)
        BpmnDiagramGraphImport.import_event_definition_elements(diagram_graph, element,
                                                                intermediate_throw_event_definitions)

    @staticmethod
    def import_boundary_event_to_graph(diagram_graph: BpmnDiagramGraph, process_id: str, element):
        """
        Adds to graph the new element that represents BPMN boundary event.
        Boundary event inherits sequence of eventDefinitionRef from Event type.
        Separate methods for each event type are required since each of them has different variants
        (Message, Error, Signal etc.).

        :param diagram_graph: a BpmnDiagramGraph object - a BPMN process diagram representation class,
        :param process_id: string object, representing an ID of process element,
        :param element: object representing a BPMN XML 'endEvent' element.
        """
        element_id = element.getAttribute(consts.Consts.id)
        boundary_event_definitions = BoundaryEventDefinitionTypes.getTypes()
        BpmnDiagramGraphImport.import_flow_node_to_graph(diagram_graph, process_id, element)

        node = diagram_graph.nodes[element_id]
        if isinstance(node, BoundaryEvent):
            node.parallel_multiple = BpmnImportUtils.convert_str_to_bool(
                element.getAttribute(consts.Consts.parallel_multiple) \
                    if element.hasAttribute(consts.Consts.parallel_multiple) else "false"
            )
            node.cancel_activity = BpmnImportUtils.convert_str_to_bool(
                element.getAttribute(consts.Consts.cancel_activity) \
                    if element.hasAttribute(consts.Consts.cancel_activity) else "true"
            )
            node.attached_to_ref = element.getAttribute(consts.Consts.attached_to_ref)

        BpmnDiagramGraphImport.import_event_definition_elements(diagram_graph, element,
                                                                boundary_event_definitions)

    @staticmethod
    def import_sequence_flow_to_graph(diagram_graph: BpmnDiagramGraph, process_id: str, flow_element: Element):
        """
        Adds a new edge to graph and a record to sequence_flows dictionary.
        Input parameter is object of class xml.dom.Element.
        Edges are identified by pair of sourceRef and targetRef attributes of BPMNFlow element. We also
        provide a dictionary, that maps sequenceFlow ID attribute with its sourceRef and targetRef.
        Method adds basic attributes of sequenceFlow element to edge. Those elements are:

        - id - added as edge attribute, we assume that this is a required value,
        - name - optional attribute, empty string by default.

        :param diagram_graph : a BpmnDiagramGraph object - a BPMN process diagram representation class,
        :param process_id: string object, representing an ID of process element,
        :param flow_element: object representing a BPMN XML 'sequenceFlow' element.
        """
        sequence_flows = diagram_graph.sequence_flows
        flow_id = flow_element.getAttribute(consts.Consts.id)
        name = flow_element.getAttribute(consts.Consts.name) if flow_element.hasAttribute(consts.Consts.name) else ""
        source_ref = flow_element.getAttribute(consts.Consts.source_ref)
        target_ref = flow_element.getAttribute(consts.Consts.target_ref)
        sequence_flows[flow_id] = SequenceFlow(id=flow_id, name=name, source_ref_id=source_ref,
                                               target_ref_id=target_ref, process_id=process_id)

        for element in utils.BpmnImportUtils.iterate_elements(flow_element):
            if element.nodeType != element.TEXT_NODE:
                tag_name = utils.BpmnImportUtils.remove_namespace_from_tag_name(element.tagName)
                if tag_name == consts.Consts.condition_expression:
                    condition_expression = element.firstChild.nodeValue
                    condition_id = element.getAttribute(consts.Consts.id)
                    sequence_flows[flow_id].condition_expression = ConditionExpression(id=condition_id,
                                                                                       condition=condition_expression)

        '''
        # Add incoming / outgoing nodes to corresponding elements. May be redundant action since this information is
        added when processing nodes, but listing incoming / outgoing nodes under node element is optional - this way
        we can make sure this info will be imported.
        '''
        if source_ref in diagram_graph.nodes:
            source_node = diagram_graph.nodes[source_ref]
            if flow_id not in source_node.outgoing:
                source_node.outgoing.append(flow_id)

        if target_ref in diagram_graph.nodes:
            target_node = diagram_graph.nodes[target_ref]
            if flow_id not in target_node.incoming:
                target_node.incoming.append(flow_id)

    @staticmethod
    def import_message_flow_to_graph(diagram_graph: BpmnDiagramGraph, flow_element: Element):
        """
        Adds a new edge to graph and a record to message flows dictionary.
        Input parameter is object of class xml.dom.Element.
        Edges are identified by pair of sourceRef and targetRef attributes of BPMNFlow element. We also
        provide a dictionary, that maps messageFlow ID attribute with its sourceRef and targetRef.
        Method adds basic attributes of messageFlow element to edge. Those elements are:

        - id - added as edge attribute, we assume that this is a required value,
        - name - optional attribute, empty string by default.

        :param diagram_graph: a BpmnDiagramGraph object - a BPMN process diagram representation class,
        :param flow_element: object representing a BPMN XML 'messageFlow' element.
        """
        message_flows = diagram_graph.message_flows
        flow_id = flow_element.getAttribute(consts.Consts.id)
        name = flow_element.getAttribute(consts.Consts.name) if flow_element.hasAttribute(consts.Consts.name) else ""
        source_ref = flow_element.getAttribute(consts.Consts.source_ref)
        target_ref = flow_element.getAttribute(consts.Consts.target_ref)
        message_flows[flow_id] = MessageFlow(id=flow_id, name=name, source_ref_id=source_ref, target_ref_id=target_ref)

        '''
        # Add incoming / outgoing nodes to corresponding elements. May be redundant action since this information is
        added when processing nodes, but listing incoming / outgoing nodes under node element is optional - this way
        we can make sure this info will be imported.
        '''
        if source_ref in diagram_graph.nodes:
            source_node = diagram_graph.nodes[source_ref]
            if flow_id not in source_node.outgoing:
                source_node.outgoing.append(flow_id)

        if target_ref in diagram_graph.nodes:
            target_node = diagram_graph.nodes[target_ref]
            if flow_id not in target_node.incoming:
                target_node.incoming.append(flow_id)

    @staticmethod
    def import_shape_di(diagram_graph: BpmnDiagramGraph, shape_element: Element):
        """
        Adds Diagram Interchange information (information about rendering a diagram) to appropriate
        BPMN diagram element in graph node.
        We assume that those attributes are required for each BPMNShape:

        - width - width of BPMNShape,
        - height - height of BPMNShape,
        - x - first coordinate of BPMNShape,
        - y - second coordinate of BPMNShape.

        :param diagram_graph: a BpmnDiagramGraph object - a BPMN process diagram representation class,
        :param shape_element: object representing a BPMN XML 'BPMNShape' element.
        """
        participants = diagram_graph.participants
        element_id = shape_element.getAttribute(consts.Consts.bpmn_element)
        bounds = shape_element.getElementsByTagNameNS("*", "Bounds")[0]
        if element_id in diagram_graph.nodes:
            node = diagram_graph.nodes[element_id]
            node.width = BpmnImportUtils.convert_str_to_float(bounds.getAttribute(consts.Consts.width))
            node.height = BpmnImportUtils.convert_str_to_float(bounds.getAttribute(consts.Consts.height))

            if isinstance(node, SubProcess):
                node.is_expanded = BpmnImportUtils.convert_str_to_bool(
                    shape_element.getAttribute(consts.Consts.is_expanded) \
                        if shape_element.hasAttribute(consts.Consts.is_expanded) else False)
            node.x = BpmnImportUtils.convert_str_to_float(bounds.getAttribute(consts.Consts.x))
            node.y = BpmnImportUtils.convert_str_to_float(bounds.getAttribute(consts.Consts.y))
        if element_id in participants:
            # BPMNShape is either connected with FlowNode or Participant
            participant = participants[element_id]
            participant.is_horizontal = BpmnImportUtils.convert_str_to_bool(
                shape_element.getAttribute(consts.Consts.is_horizontal)
            )
            participant.width = BpmnImportUtils.convert_str_to_float(bounds.getAttribute(consts.Consts.width))
            participant.height = BpmnImportUtils.convert_str_to_float(bounds.getAttribute(consts.Consts.height))
            participant.x = BpmnImportUtils.convert_str_to_float(bounds.getAttribute(consts.Consts.x))
            participant.y = BpmnImportUtils.convert_str_to_float(bounds.getAttribute(consts.Consts.y))

    @staticmethod
    def import_flow_di(diagram_graph: BpmnDiagramGraph, flow_element: minidom.Element):
        """
        Adds Diagram Interchange information (information about rendering a diagram) to appropriate
        BPMN sequence flow represented as graph edge.
        We assume that each BPMNEdge has a list of 'waypoint' elements. BPMN 2.0 XML Schema states,
        that each BPMNEdge must have at least two waypoints.

        :param diagram_graph: a BPMN process diagram representation class,
        :param flow_element: object representing a BPMN XML 'BPMNEdge' element.
        """
        sequence_flows = diagram_graph.sequence_flows
        message_flows = diagram_graph.message_flows

        flow_id = flow_element.getAttribute(consts.Consts.bpmn_element)
        waypoints_xml = flow_element.getElementsByTagNameNS("*", consts.Consts.waypoint)
        length = len(waypoints_xml)

        waypoints = [None] * length
        for index in range(length):
            waypoint_tmp = (waypoints_xml[index].getAttribute(consts.Consts.x),
                            waypoints_xml[index].getAttribute(consts.Consts.y))
            waypoints[index] = waypoint_tmp

        if flow_id in sequence_flows:
            s_flow = sequence_flows[flow_id]
            s_flow.waypoints = waypoints
        elif flow_id in message_flows:
            m_flow = message_flows[flow_id]
            m_flow.waypoints = waypoints

    @staticmethod
    def read_xml_file(filepath: str) -> minidom.Document:
        """
        Reads BPMN 2.0 XML file from given filepath and returns xml.dom.xminidom.Document object.

        :param filepath: filepath of source XML file.
        """
        dom_tree = minidom.parse(filepath)
        return dom_tree
