# coding=utf-8
"""
Implementation of exporting process to CSV functionality, as proposed in article "Spreadsheet-Based Business
Process Modeling" by Kluza k. and Wisniewski P.
"""
from __future__ import print_function

import copy
import errno
import os
import string
from typing import TextIO

import bpmn_python.bpmn_python_consts as consts
import bpmn_python.bpmn_diagram_exception as bpmn_exception
import bpmn_python.bpmn_import_utils as utils
from bpmn_python.bpmn_diagram_layouter import NodeClassification
from bpmn_python.bpmn_diagram_rep import BpmnDiagramGraph
from bpmn_python.graph.classes.activities.activity import Activity
from bpmn_python.graph.classes.activities.subprocess import SubProcess
from bpmn_python.graph.classes.activities.task import Task
from bpmn_python.graph.classes.events.end_event import EndEvent
from bpmn_python.graph.classes.events.start_event import StartEvent
from bpmn_python.graph.classes.flow_node import FlowNode, NodeType
from bpmn_python.graph.classes.gateways.exclusive_gateway import ExclusiveGateway
from bpmn_python.graph.classes.gateways.inclusive_gateway import InclusiveGateway
from bpmn_python.graph.classes.gateways.parallel_gateway import ParallelGateway
from bpmn_python.graph.classes.root_element.event_definition import EventDefinitionType


class BpmnDiagramGraphCsvExport(object):
    # TODO read user and add 'who' param
    # TODO loops
    """
    Class that provides implementation of exporting process to CSV functionality
    """
    gateways_list = ["exclusiveGateway", "inclusiveGateway", "parallelGateway"]
    tasks_list = ["task", "subProcess"]

    classification_element = "Element"
    classification_start_event = "Start Event"
    classification_end_event = "End Event"
    classification_join = "Join"
    classification_split = "Split"

    '''
    Supported start event types: normal, timer, message.
    Supported end event types: normal, message.
    '''
    events_list = ["startEvent", "endEvent"]
    lanes_list = ["process", "laneSet", "lane"]

    def __init__(self):
        pass

    @staticmethod
    def export_process_to_csv(bpmn_diagram: BpmnDiagramGraph, directory: str, filename: str):
        """
        Root method of CSV export functionality.

        :param bpmn_diagram: an instance of BpmnDiagramGraph class,
        :param directory: a string object, which is a path of output directory,
        :param filename: a string object, which is a name of output file.
        """
        nodes = copy.deepcopy(bpmn_diagram.get_nodes())
        start_nodes = []
        export_elements = []

        for node in nodes:
            incoming_list = node.incoming
            if len(incoming_list) == 0:
                start_nodes.append(node)
        if len(start_nodes) != 1:
            raise bpmn_exception.BpmnPythonError("Exporting to CSV format accepts only one start event")

        nodes_classification = utils.BpmnImportUtils.generate_nodes_clasification(bpmn_diagram)
        start_node = start_nodes.pop()
        BpmnDiagramGraphCsvExport.export_node(bpmn_diagram, export_elements, start_node, nodes_classification)

        try:
            os.makedirs(directory)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        file_object = open(directory + filename, "w")
        file_object.write("Order,Activity,Condition,Who,Subprocess,Terminated\n")
        BpmnDiagramGraphCsvExport.write_export_node_to_file(file_object, export_elements)
        file_object.close()

    @staticmethod
    def export_node(bpmn_graph: BpmnDiagramGraph,
                    export_elements: list[dict[str, str]],
                    node: FlowNode,
                    nodes_classification: dict[str, NodeClassification],
                    order: int = 0,
                    prefix: str = "",
                    condition: str = "",
                    who: str = "",
                    add_join: bool = False
                    ) -> FlowNode | None:
        """
        General method for node exporting

        :param bpmn_graph: an instance of BpmnDiagramGraph class,
        :param export_elements: a dictionary object. The key is a node ID, value is a dictionary of parameters that
               will be used in exported CSV document,
        :param node: FlowNode object,
        :param nodes_classification: dictionary of classification labels. Key - node id. Value - NodeClassification object,
        :param order: the order param of exported node,
        :param prefix: the prefix of exported node - if the task appears after some gateway, the prefix will identify
               the branch
        :param condition: the condition param of exported node,
        :param who: the condition param of exported node,
        :param add_join: boolean flag. Used to indicate if "Join" element should be added to CSV.
        :return: None or the next node object if the exported node was a gateway join.
        """
        if isinstance(node, StartEvent):
            return BpmnDiagramGraphCsvExport.export_start_event(bpmn_graph, export_elements, node, nodes_classification,
                                                                order=order, prefix=prefix, condition=condition,
                                                                who=who)
        elif isinstance(node, EndEvent):
            return BpmnDiagramGraphCsvExport.export_end_event(export_elements, node, order=order, prefix=prefix,
                                                              condition=condition, who=who)
        else:
            return BpmnDiagramGraphCsvExport.export_element(bpmn_graph, export_elements, node, nodes_classification,
                                                            order=order, prefix=prefix, condition=condition, who=who,
                                                            add_join=add_join)

    @staticmethod
    def export_element(bpmn_graph: BpmnDiagramGraph,
                       export_elements: list[dict[str, str]],
                       node: FlowNode,
                       nodes_classification: dict[str, NodeClassification],
                       order: int = 0,
                       prefix: str = "",
                       condition: str = "",
                       who: str = "",
                       add_join: bool = False
                       ) -> FlowNode | None:
        """
        Export a node with "Element" classification (task, subprocess or gateway)

        :param bpmn_graph: an instance of BpmnDiagramGraph class,
        :param export_elements: a dictionary object. The key is a node ID, value is a dictionary of parameters that
               will be used in exported CSV document,
        :param node: FlowNode object,
        :param nodes_classification: dictionary of classification labels. Key - node id. Value - NodeClassification object,
        :param order: the order param of exported node,
        :param prefix: the prefix of exported node - if the task appears after some gateway, the prefix will identify
               the branch
        :param condition: the condition param of exported node,
        :param who: the condition param of exported node,
        :param add_join: boolean flag. Used to indicate if "Join" element should be added to CSV.
        :return: None or the next node object if the exported node was a gateway join.
        """
        node_type = node.node_type
        node_classification = nodes_classification[node.id]

        outgoing_flows = node.outgoing
        if (isinstance(node, ExclusiveGateway) or isinstance(node, InclusiveGateway) or isinstance(node, Activity)) \
                and node.default is not None:
            default_flow_id = node.default
        else:
            default_flow_id = None

        if BpmnDiagramGraphCsvExport.classification_join in node_classification.classification and not add_join:
            # If the node is a join, then retract the recursion back to the split.
            # In case of activity - return current node. In case of gateway - return outgoing node
            # (we are making assumption that join has only one outgoing node)
            if isinstance(node, Task) or isinstance(node, SubProcess):
                return node
            else:
                outgoing_flow_id = outgoing_flows[0]
                _, _, outgoing_flow = bpmn_graph.get_flow_by_id(outgoing_flow_id)
                _, outgoing_node = bpmn_graph.get_node_by_id(outgoing_flow.target_ref_id)
                return outgoing_node
        else:
            if node_type == NodeType.TASK:
                export_elements.append({"Order": prefix + str(order), "Activity": node.name,
                                        "Condition": condition, "Who": who, "Subprocess": "", "Terminated": ""})
            elif node_type == NodeType.SUB_PROCESS:
                export_elements.append({"Order": prefix + str(order), "Activity": node.name,
                                        "Condition": condition, "Who": who, "Subprocess": "yes", "Terminated": ""})

        if BpmnDiagramGraphCsvExport.classification_split in node_classification.classification:
            next_node = None
            alphabet_suffix_index = 0
            for outgoing_flow_id in outgoing_flows:
                _, _, outgoing_flow = bpmn_graph.get_flow_by_id(outgoing_flow_id)
                _, outgoing_node = bpmn_graph.get_node_by_id(outgoing_flow.target_ref_id)

                # This will work only up to 26 outgoing flows
                suffix = string.ascii_lowercase[alphabet_suffix_index]
                next_prefix = prefix + str(order) + suffix
                alphabet_suffix_index += 1
                # parallel gateway does not uses conditions
                if node_type != NodeType.PARALLEL and outgoing_flow.name is not None:
                    condition = outgoing_flow.name
                else:
                    condition = ""

                if BpmnDiagramGraphCsvExport.classification_join in nodes_classification[outgoing_node.id]:
                    export_elements.append(
                        {"Order": next_prefix + str(1), "Activity": "goto " + prefix + str(order + 1),
                         "Condition": condition, "Who": who, "Subprocess": "", "Terminated": ""})
                elif outgoing_flow_id == default_flow_id:
                    tmp_next_node = BpmnDiagramGraphCsvExport.export_node(bpmn_graph, export_elements, outgoing_node,
                                                                          nodes_classification, 1, next_prefix, "else",
                                                                          who)
                    if tmp_next_node is not None:
                        next_node = tmp_next_node
                else:
                    tmp_next_node = BpmnDiagramGraphCsvExport.export_node(bpmn_graph, export_elements, outgoing_node,
                                                                          nodes_classification, 1, next_prefix,
                                                                          condition, who)
                    if tmp_next_node is not None:
                        next_node = tmp_next_node

            if next_node is not None:
                return BpmnDiagramGraphCsvExport.export_node(bpmn_graph, export_elements, next_node,
                                                             nodes_classification, order=(order + 1), prefix=prefix,
                                                             who=who, add_join=True)

        elif len(outgoing_flows) == 1:
            outgoing_flow_id = outgoing_flows[0]
            _, _, outgoing_flow = bpmn_graph.get_flow_by_id(outgoing_flow_id)
            _, outgoing_node = bpmn_graph.get_node_by_id(outgoing_flow.target_ref_id)
            return BpmnDiagramGraphCsvExport.export_node(bpmn_graph, export_elements, outgoing_node,
                                                         nodes_classification, order=(order + 1), prefix=prefix,
                                                         who=who)
        else:
            return None

    @staticmethod
    def export_start_event(bpmn_graph: BpmnDiagramGraph,
                           export_elements: list[dict[str, str]],
                           node: StartEvent,
                           nodes_classification: dict[str, NodeClassification],
                           order: int = 0,
                           prefix: str = "",
                           condition: str = "",
                           who: str = ""
                           ) -> FlowNode | None:
        """
        Start event export

        :param bpmn_graph: an instance of BpmnDiagramGraph class,
        :param export_elements: a dictionary object. The key is a node ID, value is a dictionary of parameters that
               will be used in exported CSV document,
        :param node: FlowNode object,
        :param order: the order param of exported node,
        :param nodes_classification: dictionary of classification labels. Key - node id. Value - a list of labels,
        :param prefix: the prefix of exported node - if the task appears after some gateway, the prefix will identify
               the branch
        :param condition: the condition param of exported node,
        :param who: the condition param of exported node,
        :return: None or the next node object if the exported node was a gateway join.
        """

        # Assuming that there is only one event definition
        event_definitions = node.event_definition_list
        if event_definitions is not None and len(event_definitions) > 0:
            event_definition = event_definitions[0]
        else:
            event_definition = None

        if event_definition.definition_type == EventDefinitionType.MESSAGE:
            activity = "message " + node.name
        elif event_definition.definition_type == EventDefinitionType.TIMER:
            activity = "timer " + node.name
        else:
            activity = node.name

        export_elements.append({"Order": prefix + str(order), "Activity": activity, "Condition": condition,
                                "Who": who, "Subprocess": "", "Terminated": ""})

        outgoing_flow_id = node.outgoing[0]
        _, _, outgoing_flow = bpmn_graph.get_flow_by_id(outgoing_flow_id)
        _, outgoing_node = bpmn_graph.get_node_by_id(outgoing_flow.target_ref_id)
        return BpmnDiagramGraphCsvExport.export_node(bpmn_graph, export_elements, outgoing_node, nodes_classification,
                                                     order + 1, prefix, who)

    @staticmethod
    def export_end_event(export_elements: list[dict[str, str]],
                         node: EndEvent,
                         order: int = 0,
                         prefix: str = "",
                         condition: str = "",
                         who: str = ""
                         ) -> FlowNode | None:
        """
        End event export

        :param export_elements: a dictionary object. The key is a node ID, value is a dictionary of parameters that
               will be used in exported CSV document,
        :param node: FlowNode object,
        :param order: the order param of exported node,
        :param prefix: the prefix of exported node - if the task appears after some gateway, the prefix will identify
               the branch
        :param condition: the condition param of exported node,
        :param who: the condition param of exported node,
        :return: None or the next node object if the exported node was a gateway join.
        """

        # Assuming that there is only one event definition
        event_definitions = node.event_definition_list
        if event_definitions is not None and len(event_definitions) > 0:
            event_definition = event_definitions[0]
        else:
            event_definition = None

        if event_definition.definition_type == EventDefinitionType.MESSAGE:
            activity = "message " + node.name
        else:
            activity = node.name

        export_elements.append({"Order": prefix + str(order), "Activity": activity, "Condition": condition, "Who": who,
                                "Subprocess": "", "Terminated": "yes"})
        # No outgoing elements for EndEvent
        return None

    @staticmethod
    def write_export_node_to_file(file_object: TextIO, export_elements: list[dict[str, str]]):
        """
        Exporting process to CSV file

        :param file_object: object of File class,
        :param export_elements: a dictionary object. The key is a node ID, value is a dictionary of parameters that
               will be used in exported CSV document.
        """
        for export_element in export_elements:
            # Order,Activity,Condition,Who,Subprocess,Terminated
            file_object.write(
                export_element["Order"] + "," + export_element["Activity"] + "," + export_element["Condition"] + "," +
                export_element["Who"] + "," + export_element["Subprocess"] + "," + export_element["Terminated"] + "\n")
