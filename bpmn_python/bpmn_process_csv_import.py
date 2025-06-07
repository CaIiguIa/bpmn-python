# coding=utf-8
"""
Implementation of exporting process to CSV functionality, as proposed in article "Spreadsheet-Based Business
Process Modeling" by Kluza k. and Wisniewski P.
"""
from __future__ import print_function

import copy

import pandas as pd
import re
import six

import bpmn_python.bpmn_python_consts as consts
import bpmn_python.bpmn_diagram_exception as bpmn_exception
from bpmn_python.bpmn_diagram_rep import BpmnDiagramGraph
from bpmn_python.graph.classes.condition_expression import ConditionExpression
from bpmn_python.graph.classes.flow_node import NodeType
from bpmn_python.graph.classes.root_element.process import Process, ProcessType
from bpmn_python.graph.classes.sequence_flow import SequenceFlow

regex_pa_trailing_number = r'^(.*[a-z|A-Z]|[^0-9]?)([0-9]+)$'
regex_pa_trailing_letter = r'(.+)([a-z|A-Z])'
regex_pa_merge_node_finder = r'(.*?)([0-9]+[a-z|A-Z])(.*?)'
regex_pa_num_let = r'([0-9]+)([a-z,A-Z])'
regex_prefix_split_succ = r'^'
regex_suffix_split_succ = r'([a-z|A-Z]|[a-z|A-Z][1]+)$'

default_process_id = 'process_1'
default_plane_id = 'plane_1'


def get_node_type(order: str, csv_line_dict: dict[str, str]) -> NodeType:
    """
    Determines the type of node based on its order and attributes in the CSV line.

    :param order: A string representing the node's order in the process.
    :param csv_line_dict: A dictionary containing attributes of the node from the CSV file.
    :return: A string representing the node type (e.g., start event, end event, task, etc.).
    """
    if order == str(0):
        return NodeType.START
    if csv_line_dict[consts.Consts.csv_terminated] == 'yes':
        return NodeType.END
    if csv_line_dict[consts.Consts.csv_subprocess] == 'yes':
        return NodeType.SUB_PROCESS
    else:
        return NodeType.TASK


def add_node_info_to_diagram_graph(order: str,
                                   node_type: NodeType | None,
                                   activity: str,
                                   process_id: str,
                                   bpmn_diagram: BpmnDiagramGraph
                                   ):
    """
    Adds or modifies a node in the BPMN diagram graph based on the provided parameters.

    :param order: A string representing the node ID in the graph.
    :param node_type: The type of the node (e.g., start event, task, gateway, etc.).
    :param activity: The name of the activity associated with the node.
    :param process_id: The ID of the process to which the node belongs.
    :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
    """
    if node_type == NodeType.START:
        bpmn_diagram.add_modify_start_event_to_diagram(process_id, start_event_name=activity, node_id=order)
    elif node_type == NodeType.END:
        bpmn_diagram.add_modify_end_event_to_diagram(process_id, node_id=order)
    elif node_type == NodeType.SUB_PROCESS:
        bpmn_diagram.add_subprocess_to_diagram(process_id, subprocess_name=activity, node_id=order)
    elif node_type == NodeType.INCLUSIVE:
        bpmn_diagram.add_modify_gateway_to_diagram(process_id, node_id=order,
                                                   gateway_type=NodeType.INCLUSIVE)
    elif node_type == NodeType.EXCLUSIVE:
        bpmn_diagram.add_modify_gateway_to_diagram(process_id, node_id=order,
                                                   gateway_type=NodeType.EXCLUSIVE)
    elif node_type == NodeType.PARALLEL:
        bpmn_diagram.add_modify_gateway_to_diagram(process_id, node_id=order, gateway_type=NodeType.PARALLEL)
    else:
        bpmn_diagram.add_modify_task_to_diagram(process_id, task_name=activity, node_id=order)


def import_nodes_info(process_dict: dict[str, dict[str, str]], bpmn_diagram: BpmnDiagramGraph):
    """
    Iterates through the process dictionary, determines the type of each node,
    and adds the corresponding node information to the BPMN diagram.

    :param process_dict: A dictionary where keys are node IDs and values are dictionaries
                         containing node attributes.
    :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
    """
    for order, csv_line_dict in process_dict.items():
        node_type = get_node_type(order, csv_line_dict)
        activity = process_dict[order][consts.Consts.csv_activity]
        process_id = default_process_id
        add_node_info_to_diagram_graph(order, node_type, activity, process_id, bpmn_diagram)


def remove_white_spaces_in_orders(process_dict: dict[any, dict[str, str]]):
    """
    Removes leading and trailing white spaces from the keys in the process dictionary. Input dictionary is changed in place.

    :param process_dict: A dictionary where keys represent process orders and values contain node attributes.
    """
    tmp_process_dict = copy.deepcopy(process_dict)
    for order, csv_line_dict in tmp_process_dict.items():
        del process_dict[order]
        if isinstance(order, six.string_types) and order.strip() != order:
            process_dict[order.strip()] = csv_line_dict
        else:
            process_dict[str(order)] = csv_line_dict


def get_possible_sequence_continuation_successor(node_id: str) -> list[str]:
    """
    Analyzes the node identifier to find its possible successors in the sequence based on a numbering pattern.

    :param node_id: The identifier of the node as a string.
    :return: A list of possible sequence successor identifiers.
    """
    result = re.match(regex_pa_trailing_number, node_id)
    if result:
        last_number_in_order = result.group(2)
        next_number = str(int(last_number_in_order) + 1)
        prefix = result.group(1)
        return [prefix + next_number]
    else:
        # possible if e.g. 4a
        return []


def get_possible_split_continuation_successor(node_id: str) -> list[str]:
    """
    Determines potential successors in the case of a split, based on a numbering pattern.

    :param node_id: The identifier of the node as a string.
    :return: A list of possible split continuation successor identifiers.
    """
    result = re.match(regex_pa_trailing_number, node_id)
    if result:
        trailing_number = result.group(2)
        prefix = result.group(1)
        new_trailing_number = str(int(trailing_number) + 1)
        new_node_id = prefix + new_trailing_number
        return [new_node_id + 'a', new_node_id + 'a1']
    else:
        return []


def get_possible_merge_continuation_successors(node_id_arg: str) -> list[str]:
    """
    Determines potential successors in the case of a merge, based on a numbering and letter pattern.

    :param node_id_arg: The identifier of the node as a string.
    :return: A list of possible merge continuation successor identifiers.
    """
    node_id = copy.deepcopy(node_id_arg)
    result_trailing_number = re.match(regex_pa_trailing_number, node_id)
    if result_trailing_number:
        node_id = result_trailing_number.group(1)

    result_trailing_letter = re.match(regex_pa_trailing_letter, node_id)
    if result_trailing_letter:
        possible_successors = []
        for result in re.finditer(regex_pa_merge_node_finder, node_id):
            num_let_pair = result.group(2)
            prefix = result.group(1)
            num_let_result = re.match(regex_pa_num_let, num_let_pair)
            num = num_let_result.group(1)
            inc_num = str(int(num) + 1)
            possible_successors.append(prefix + inc_num)
        return possible_successors
    else:
        return []


def is_any_possible_successor_present_in_node_ids(possible_successors: list[str], nodes_ids: list[str]) -> bool:
    """
    Checks if any of the possible successors are present in the given list of node IDs.

    :param possible_successors: A list of potential successor node IDs.
    :param nodes_ids: A list of existing node IDs.
    :return: True if at least one possible successor is present in the list of node IDs, otherwise False.
    """
    return len(get_possible_successors_set_present_in_node_ids(possible_successors, nodes_ids)) > 0


def get_possible_successors_set_present_in_node_ids(possible_successors: list[str], nodes_ids: list[str]) -> set[str]:
    """
    Identifies which of the potential successor node IDs exist in the provided list of node IDs.

    :param possible_successors: A list of potential successor node IDs.
    :param nodes_ids: A list of existing node IDs.
    :return: A set of node IDs that are both in the possible successors and the given node IDs.
    """
    return set(possible_successors).intersection(set(nodes_ids))


def get_possible_successor_present_in_node_ids_or_raise_excp(possible_successors_node_id: list[str],
                                                             nodes_ids: list[str]) -> str:
    """
    Checks if exactly one of the possible successor node IDs exists in the provided list of node IDs.
    Raises an exception if no successor or more than one successor is found.

    :param possible_successors_node_id: A list of potential successor node IDs.
    :param nodes_ids: A list of existing node IDs.
    :return: The single node ID that is both in the possible successors and the given node IDs.
    :raises BpmnPythonError: If there is not exactly one matching successor.
    """
    possible_successor_set = get_possible_successors_set_present_in_node_ids(possible_successors_node_id, nodes_ids)
    if len(possible_successor_set) != 1:
        raise bpmn_exception.BpmnPythonError("Some error in program - there should be exactly one found successor.")
    else:
        return possible_successor_set.pop()


def get_all_split_successors(node_id: str, nodes_ids: list[str]) -> list[str]:
    """
    Identifies all possible successors of a node in the case of a split, based on a specific pattern.

    :param node_id: The identifier of the node as a string.
    :param nodes_ids: A list of existing node identifiers.
    :return: A list of node identifiers that are split successors of the given node.
    """
    result = re.match(regex_pa_trailing_number, node_id)
    if not result:
        raise bpmn_exception.BpmnPythonError("Something wrong in program - look for " + node_id)
    trailing_number = result.group(2)
    prefix = result.group(1)
    new_trailing_number = str(int(trailing_number) + 1)
    next_node_id = prefix + new_trailing_number

    pattern = regex_prefix_split_succ + next_node_id + regex_suffix_split_succ
    split_successors = []
    for elem in nodes_ids:
        if re.match(pattern, elem):
            split_successors.append(elem)
    return split_successors


def is_there_sequence_continuation(node_id: str, nodes_ids: list[str]) -> bool:
    """
    Checks if there is a sequence continuation for the given node identifier.

    :param node_id: The identifier of the node as a string.
    :param nodes_ids: A list of existing node identifiers.
    :return: True if there is a sequence continuation, otherwise False.
    """
    possible_seq_succ = get_possible_sequence_continuation_successor(node_id)
    return is_any_possible_successor_present_in_node_ids(possible_seq_succ, nodes_ids)


def is_there_split_continuation(node_id: str, nodes_ids: list[str]) -> bool:
    """
    Checks if there is a split continuation for the given node identifier.

    :param node_id: The identifier of the node as a string.
    :param nodes_ids: A list of existing node identifiers.
    :return: True if there is a split continuation, otherwise False.
    """
    possible_split_succ = get_possible_split_continuation_successor(node_id)
    return is_any_possible_successor_present_in_node_ids(possible_split_succ, nodes_ids)


def is_there_merge_continuation(node_id: str, nodes_ids: list[str]) -> bool:
    """
    Determines if there is a merge continuation for the given node identifier.

    :param node_id: The identifier of the node as a string.
    :param nodes_ids: A list of existing node identifiers.
    :return: True if there is a merge continuation, otherwise False.
    """
    possible_merge_succ = get_possible_merge_continuation_successors(node_id)
    return is_any_possible_successor_present_in_node_ids(possible_merge_succ, nodes_ids)


def is_node_the_end_event(node_id: str, process_dict: dict[str, dict[str, str]]) -> bool:
    """
    Checks if the given node is marked as an end event in the process dictionary.

    :param node_id: The identifier of the node as a string.
    :param process_dict: A dictionary containing process information.
    :return: True if the node is an end event, otherwise False.
    """
    return process_dict[node_id][consts.Consts.csv_terminated] == 'yes'


def add_outgoing_flow(node_id: str, successor_node_id: str, bpmn_diagram: BpmnDiagramGraph):
    """
    Adds an outgoing flow from the given node to its successor in the BPMN diagram.

    :param node_id: The identifier of the node as a string.
    :param successor_node_id: The identifier of the successor node as a string.
    :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
    """
    bpmn_diagram.nodes[node_id].outgoing \
        .append(get_flow_id(node_id, successor_node_id))


def add_incoming_flow(node_id: str, from_node_id: str, bpmn_diagram: BpmnDiagramGraph):
    """
    Adds an incoming flow to the given node from its predecessor in the BPMN diagram.

    :param node_id: The identifier of the node as a string.
    :param from_node_id: The identifier of the predecessor node as a string.
    :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
    """
    bpmn_diagram.nodes[node_id].incoming \
        .append(get_flow_id(from_node_id, node_id))


def get_connection_condition_if_present(to_node_id: str, process_dict: dict[str, dict[str, str]]) -> str | None:
    """
    Retrieves the connection condition for the given node if it exists in the process dictionary.

    :param to_node_id: The identifier of the node as a string.
    :param process_dict: A dictionary containing process information.
    :return: The connection condition as a string if present, otherwise None.
    """
    if to_node_id in process_dict:
        return process_dict[to_node_id].get(consts.Consts.csv_condition)


def get_flow_id(from_node_id: str, to_node_id: str) -> str:
    """
    Generates a unique flow identifier based on the source and target node IDs.

    :param from_node_id: The identifier of the source node as a string.
    :param to_node_id: The identifier of the target node as a string.
    :return: A string representing the unique flow identifier.
    """
    return from_node_id + "__" + to_node_id


def add_edge(from_node_id: str,
             to_node_id: str,
             process_dict: dict[str, dict[str, str]],
             bpmn_diagram: BpmnDiagramGraph,
             sequence_flows: dict[str, SequenceFlow]
             ):
    """
    Adds an edge (connection) between two nodes in the BPMN diagram.

    :param from_node_id: The identifier of the source node as a string.
    :param to_node_id: The identifier of the target node as a string.
    :param process_dict: A dictionary containing process information.
    :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
    :param sequence_flows: A dictionary to store sequence flow information.
    """
    condition = get_connection_condition_if_present(to_node_id, process_dict)
    flow_id = get_flow_id(from_node_id, to_node_id)
    flow = SequenceFlow(id=flow_id,
                        name="",
                        source_ref_id=from_node_id,
                        target_ref_id=to_node_id,
                        process_id=default_process_id)
    sequence_flows[flow_id] = flow

    if bool(condition):
        flow.condition_expression = ConditionExpression(id=flow_id + "_cond", condition=condition)


def add_connection(from_node_id: str,
                   to_node_id: str,
                   process_dict: dict[str, dict[str, str]],
                   bpmn_diagram: BpmnDiagramGraph,
                   sequence_flows: dict[str, SequenceFlow]
                   ):
    """
    Adds a connection between two nodes in the BPMN diagram, including outgoing and incoming flows.

    :param from_node_id: The identifier of the source node as a string.
    :param to_node_id: The identifier of the target node as a string.
    :param process_dict: A dictionary containing process information.
    :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
    :param sequence_flows: A dictionary to store sequence flow information.
    """
    add_outgoing_flow(from_node_id, to_node_id, bpmn_diagram)
    add_incoming_flow(to_node_id, from_node_id, bpmn_diagram)
    add_edge(from_node_id, to_node_id, process_dict, bpmn_diagram, sequence_flows)


def get_node_conditions(split_successors: list[str], process_dict: dict[str, dict[str, str]]):
    """
    Retrieves the conditions for the given split successors from the process dictionary.

    :param split_successors: A list of split successor node IDs.
    :param process_dict: A dictionary containing process information.
    :return: A list of conditions for the split successors.
    """
    conditions = []
    for succ in split_successors:
        conditions.append(process_dict[succ][consts.Consts.csv_condition].strip())
    return conditions


def yes_no_conditions(node_conditions: list[str]) -> bool:
    """
    Checks if the given node conditions are exactly "yes" and "no".

    :param node_conditions: A list of node conditions.
    :return: True if the conditions are exactly "yes" and "no", otherwise False.
    """
    return set(node_conditions) == {"yes", "no"}


def sth_else_conditions(node_conditions: list[str]):
    """
    Checks if the given node conditions contain "else".

    :param node_conditions: A list of node conditions.
    :return: True if the conditions contain "else", otherwise False.
    """
    return "else" in node_conditions


def no_conditions(node_conditions: list[str]) -> bool:
    """
    Checks if the given node conditions are empty or contain only empty strings.

    :param node_conditions: A list of node conditions.
    :return: True if the conditions are empty or contain only empty strings, otherwise False.
    """
    for node in node_conditions:
        if bool(node):
            return False
    return True


def get_gateway_type(node_id_to_add_after: str, nodes_ids: list[str], process_dict: dict[str, dict[str, str]]) -> NodeType:
    """
    Determines the type of gateway to be added after the given node based on its successors' conditions.

    :param node_id_to_add_after: The identifier of the node to add the gateway after.
    :param nodes_ids: A list of existing node identifiers.
    :param process_dict: A dictionary containing process information.
    :return: A string representing the gateway type (e.g., exclusive, inclusive, parallel).
    """
    split_successors = get_all_split_successors(node_id_to_add_after, nodes_ids)
    successors_conditions = get_node_conditions(split_successors, process_dict)
    if len(split_successors) == 2:
        if yes_no_conditions(successors_conditions) or sth_else_conditions(successors_conditions):
            return NodeType.EXCLUSIVE
    if no_conditions(successors_conditions):
        return NodeType.PARALLEL
    return NodeType.INCLUSIVE


def add_split_gateway(node_id_to_add_after: str,
                      nodes_ids: list[str],
                      process_dict: dict[str, dict[str, str]],
                      bpmn_diagram: BpmnDiagramGraph
                      ) -> str:
    """
    Adds a split gateway after the given node in the BPMN diagram.

    :param node_id_to_add_after: The identifier of the node to add the gateway after.
    :param nodes_ids: A list of existing node identifiers.
    :param process_dict: A dictionary containing process information.
    :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
    :return: The identifier of the added split gateway.
    """
    split_gateway_id = node_id_to_add_after + "_split"
    process_id = default_process_id
    gateway_type = get_gateway_type(node_id_to_add_after, nodes_ids, process_dict)
    activity = ""
    add_node_info_to_diagram_graph(split_gateway_id, gateway_type, activity, process_id, bpmn_diagram)
    return split_gateway_id


def get_merge_node_type(merge_successor_id: str, bpmn_diagram: BpmnDiagramGraph) -> NodeType | None:
    """
    Determines the type of merge node based on the given merge successor ID.

    :param merge_successor_id: The identifier of the merge successor node.
    :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
    :return: A string representing the merge node type (e.g., inclusive, exclusive).
    """
    result = re.match(regex_pa_trailing_number, merge_successor_id)
    if result:
        trailing_number = result.group(2)
        prev_prev_number = int(trailing_number) - 2
        if prev_prev_number < 0:
            raise bpmn_exception.BpmnPythonError("Something wrong in csv file syntax - look for " + merge_successor_id)
        prefix = result.group(1)
        split_node_id = prefix + str(prev_prev_number) + "_split"
        if split_node_id in bpmn_diagram.nodes:
            node_type = bpmn_diagram.nodes[split_node_id].node_type
            if node_type != NodeType.BASE:
                return node_type
        return NodeType.INCLUSIVE


def add_merge_gateway_if_not_exists(merge_successor_id: str, bpmn_diagram: BpmnDiagramGraph) -> tuple[str, bool]:
    """
    Adds a merge gateway if it does not already exist in the BPMN diagram.

    :param merge_successor_id: The identifier of the merge successor node.
    :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
    :return: A tuple containing the merge gateway ID and a boolean indicating if it was just created.
    """
    merge_gateway_id = merge_successor_id + "_join"
    if merge_gateway_id in bpmn_diagram.nodes:
        just_created = False
        return merge_gateway_id, just_created
    else:
        just_created = True
        process_id = default_process_id
        gateway_type = get_merge_node_type(merge_successor_id, bpmn_diagram)
        activity = ""
        add_node_info_to_diagram_graph(merge_gateway_id, gateway_type, activity, process_id, bpmn_diagram)
        return merge_gateway_id, just_created


def fill_graph_connections(process_dict: dict[str, dict[str, str]],
                           bpmn_diagram: BpmnDiagramGraph,
                           sequence_flows: dict[str, SequenceFlow]
                           ):
    """
    Fills the BPMN diagram with connections based on the process dictionary.

    :param process_dict: A dictionary containing process information.
    :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
    :param sequence_flows: A dictionary to store sequence flow information.
    """
    nodes_ids = list(bpmn_diagram.nodes.keys())
    nodes_ids_to_process = copy.deepcopy(nodes_ids)
    while len(nodes_ids_to_process) > 0:
        node_id = str(nodes_ids_to_process.pop(0))
        if is_node_the_end_event(node_id, process_dict):
            pass
        elif is_there_sequence_continuation(node_id, nodes_ids):
            possible_sequence_successors = get_possible_sequence_continuation_successor(node_id)
            successor_node_id = get_possible_successor_present_in_node_ids_or_raise_excp(possible_sequence_successors,
                                                                                         nodes_ids)
            add_connection(node_id, successor_node_id, process_dict, bpmn_diagram, sequence_flows)
        elif is_there_split_continuation(node_id, nodes_ids):
            split_gateway_id = add_split_gateway(node_id, nodes_ids, process_dict, bpmn_diagram)
            add_connection(node_id, split_gateway_id, process_dict, bpmn_diagram, sequence_flows)
            for successor_node_id in get_all_split_successors(node_id, nodes_ids):
                add_connection(split_gateway_id, successor_node_id, process_dict, bpmn_diagram, sequence_flows)
            pass
        elif is_there_merge_continuation(node_id, nodes_ids):
            possible_merge_successors = get_possible_merge_continuation_successors(node_id)
            merge_successor_id = get_possible_successor_present_in_node_ids_or_raise_excp(possible_merge_successors,
                                                                                          nodes_ids)
            merge_gateway_id, just_created = add_merge_gateway_if_not_exists(merge_successor_id, bpmn_diagram)
            if just_created:
                add_connection(merge_gateway_id, merge_successor_id, process_dict, bpmn_diagram, sequence_flows)
            add_connection(node_id, merge_gateway_id, process_dict, bpmn_diagram, sequence_flows)
        else:
            raise bpmn_exception.BpmnPythonError("Something wrong in csv file syntax - look for " + node_id)


def remove_outgoing_connection(base_node: str,
                               bpmn_diagram: BpmnDiagramGraph,
                               sequence_flows: dict[str, SequenceFlow]
                               ) -> str:
    """
    Removes the outgoing connection from the given base node in the BPMN diagram.

    :param base_node: The identifier of the base node as a string.
    :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
    :param sequence_flows: A dictionary to store sequence flow information.
    :return: The identifier of the neighbor node that was connected to the base node.
    """
    outgoing_flow_id = bpmn_diagram.nodes[base_node].outgoing[0]
    neighbour_node = sequence_flows[outgoing_flow_id].target_ref_id
    bpmn_diagram.nodes[neighbour_node].incoming.remove(outgoing_flow_id)
    del sequence_flows[outgoing_flow_id]
    return neighbour_node


def remove_incoming_connection(base_node: str,
                               bpmn_diagram: BpmnDiagramGraph,
                               sequence_flows: dict[str, SequenceFlow]) -> str:
    """
    Removes the incoming connection to the given base node in the BPMN diagram.

    :param base_node: The identifier of the base node as a string.
    :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
    :param sequence_flows: A dictionary to store sequence flow information.
    :return: The identifier of the neighbor node that was connected to the base node.
    """
    incoming_flow_id = bpmn_diagram.nodes[base_node].incoming[0]
    neighbour_node = sequence_flows[incoming_flow_id].source_ref_id
    bpmn_diagram.nodes[neighbour_node].outgoing.remove(incoming_flow_id)
    del sequence_flows[incoming_flow_id]
    return neighbour_node


def remove_node(node_id_to_remove: str,
                process_dict: dict[str, dict[str, str]],
                bpmn_diagram: BpmnDiagramGraph,
                sequence_flows: dict[str, SequenceFlow]
                ) -> tuple[str, str]:
    """
    Removes the given node from the BPMN diagram and updates the process dictionary and sequence flows.

    :param node_id_to_remove: The identifier of the node to remove.
    :param process_dict: A dictionary containing process information.
    :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
    :param sequence_flows: A dictionary to store sequence flow information.
    :return: A tuple containing the new source and target nodes after removal.
    """
    new_source_node = remove_incoming_connection(node_id_to_remove, bpmn_diagram, sequence_flows)
    new_target_node = remove_outgoing_connection(node_id_to_remove, bpmn_diagram, sequence_flows)
    del bpmn_diagram.nodes[node_id_to_remove]
    process_dict.pop(node_id_to_remove, None)
    # add new connection
    return new_source_node, new_target_node


def remove_unnecessary_merge_gateways(process_dict: dict[str, dict[str, str]],
                                      bpmn_diagram: BpmnDiagramGraph,
                                      sequence_flows: dict[str, SequenceFlow]
                                      ):
    """
    Removes unnecessary merge gateways from the BPMN diagram.

    :param process_dict: A dictionary containing process information.
    :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
    :param sequence_flows: A dictionary to store sequence flow information.
    """
    for node in bpmn_diagram.get_nodes():
        gateway_type = node.node_type
        if gateway_type in [NodeType.INCLUSIVE, NodeType.EXCLUSIVE, NodeType.PARALLEL]:
            if len(node.incoming) < 2 and len(node.outgoing) < 2:
                new_source_node, new_target_node = remove_node(node.id, process_dict, bpmn_diagram, sequence_flows)
                add_connection(new_source_node, new_target_node, process_dict, bpmn_diagram, sequence_flows)


def remove_goto_nodes(process_dict: dict[str, dict[str, str]],
                      bpmn_diagram: BpmnDiagramGraph,
                      sequence_flows: dict[str, SequenceFlow]
                      ):
    """
    Removes "goto" nodes from the BPMN diagram and updates the process dictionary and sequence flows.

    :param process_dict: A dictionary containing process information.
    :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
    :param sequence_flows: A dictionary to store sequence flow information.
    """
    for order, csv_line_dict in copy.deepcopy(process_dict).items():
        if csv_line_dict[consts.Consts.csv_activity].lower().startswith("goto"):
            source_node, _ = remove_node(order, process_dict, bpmn_diagram, sequence_flows)
            target_node = csv_line_dict[consts.Consts.csv_activity].strip().split()[1]
            add_connection(source_node, target_node, process_dict, bpmn_diagram, sequence_flows)


class BpmnDiagramGraphCSVImport(object):
    """
    Template
    """

    @staticmethod
    def load_diagram_from_csv(filepath: str, bpmn_diagram: BpmnDiagramGraph):
        """
        Reads an CSV file from given filepath and maps it into inner representation of BPMN diagram.
        Returns an instance of BPMNDiagramGraph class.

        :param filepath: string with output filepath,
        :param bpmn_diagram: an instance of BpmnDiagramGraph class.
        """
        sequence_flows = bpmn_diagram.sequence_flows
        process_elements_dict = bpmn_diagram.process_elements
        diagram_attributes = bpmn_diagram.diagram_attributes
        plane_attributes = bpmn_diagram.plane_attributes

        process_dict = BpmnDiagramGraphCSVImport.import_csv_file_as_dict(filepath)

        BpmnDiagramGraphCSVImport.populate_diagram_elements_dict(diagram_attributes)
        BpmnDiagramGraphCSVImport.populate_process_elements_dict(process_elements_dict)
        BpmnDiagramGraphCSVImport.populate_plane_elements_dict(plane_attributes)

        BpmnDiagramGraphCSVImport.import_nodes(process_dict, bpmn_diagram, sequence_flows)
        BpmnDiagramGraphCSVImport.representation_adjustment(process_dict, bpmn_diagram, sequence_flows)

    @staticmethod
    def import_csv_file_as_dict(filepath: str) -> dict[str, dict[str, str]]:
        """
        Imports a CSV file as a dictionary.

        :param filepath: The path to the CSV file.
        :return: A dictionary representation of the CSV file.
        """
        process_dict = pd.read_csv(filepath, index_col=0).fillna("").to_dict('index')
        remove_white_spaces_in_orders(process_dict)
        return process_dict

    @staticmethod
    def get_given_task_as_dict(csv_df, order_val):
        """
        Retrieves a specific task from the CSV DataFrame as a dictionary.

        :param csv_df: The CSV DataFrame.
        :param order_val: The order value of the task to retrieve.
        :return: A dictionary representation of the task.
        """
        return csv_df.loc[csv_df[consts.Consts.csv_order] == order_val].iloc[0].to_dict()

    @staticmethod
    def import_nodes(process_dict: dict[str, dict[str, str]],
                     bpmn_diagram: BpmnDiagramGraph,
                     sequence_flows: dict[str, SequenceFlow]
                     ):
        """
        Imports nodes into the BPMN diagram based on the process dictionary.

        :param process_dict: A dictionary containing process information.
        :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
        :param sequence_flows: A dictionary to store sequence flow information.
        """
        import_nodes_info(process_dict, bpmn_diagram)
        fill_graph_connections(process_dict, bpmn_diagram, sequence_flows)

    @staticmethod
    def populate_diagram_elements_dict(diagram_elements_dict: dict[str, str]):
        """
        Populates the diagram elements dictionary with default values.

        :param diagram_elements_dict: The dictionary to populate.
        """
        diagram_elements_dict[consts.Consts.id] = "diagram1"
        diagram_elements_dict[consts.Consts.name] = "diagram_name"

    @staticmethod
    def populate_process_elements_dict(process_elements_dict: dict[str, Process]):
        """
        Populates the process elements dictionary with default values and process information.

        :param process_elements_dict: The dictionary to populate.
        """
        process_id = default_process_id
        process = Process(id=default_process_id, name="", is_closed=False, is_executable=False,
                          process_type=ProcessType.NONE)
        process_elements_dict[process_id] = process

    @staticmethod
    def populate_plane_elements_dict(plane_elements_dict: dict[str, str]):
        """
        Populates the plane elements dictionary with default values.

        :param plane_elements_dict: The dictionary to populate.
        """
        plane_elements_dict[consts.Consts.id] = default_plane_id
        plane_elements_dict[consts.Consts.bpmn_element] = default_process_id

    @staticmethod
    def representation_adjustment(process_dict: dict[str, dict[str, str]],
                                  bpmn_diagram: BpmnDiagramGraph,
                                  sequence_flows: dict[str, SequenceFlow]
                                  ):
        """
        Adjusts the representation of the BPMN diagram.

        :param process_dict: A dictionary containing process information.
        :param bpmn_diagram: An instance of the BPMNDiagramGraph class representing the BPMN diagram.
        :param sequence_flows: A dictionary to store sequence flow information.
        """
        remove_goto_nodes(process_dict, bpmn_diagram, sequence_flows)
        remove_unnecessary_merge_gateways(process_dict, bpmn_diagram, sequence_flows)
