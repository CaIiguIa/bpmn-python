# coding=utf-8
"""
Collection of different metrics used to compare diagram layout quality
"""
import copy
import bpmn_python.bpmn_python_consts as consts
from bpmn_python.bpmn_diagram_rep import BpmnDiagramGraph
from bpmn_python.graph.classes.flow_node import FlowNode, NodeType
from bpmn_python.graph.classes.sequence_flow import SequenceFlow


def count_crossing_points(bpmn_graph: BpmnDiagramGraph) -> int:
    """
    Counts the number of crossing points between flow segments in the BPMN graph.

    :param bpmn_graph: The BPMN graph object.
    :return: The number of crossing points.
    """
    flows = [flow for _, _, flow in bpmn_graph.get_flows()]
    segments = get_flows_segments(flows)

    crossing_point_num = 0
    while segments:
        segment_one = segments.pop()
        for segment_two in segments:
            if segments_common_points(segment_one, segment_two) is False and do_intersect(segment_one, segment_two):
                crossing_point_num += 1

    return crossing_point_num


def compute_determinant(p1: tuple[float, float], p2: tuple[float, float], p3: tuple[float, float]) -> float:
    """
    Computes the determinant of three points in a 2D space.

    :param p1: First point as a tuple (x, y).
    :param p2: Second point as a tuple (x, y).
    :param p3: Third point as a tuple (x, y).
    :return: The determinant value.
    """
    det = float(p1[0]) * float(p2[1]) + float(p2[0]) * float(p3[1]) + float(p3[0]) * float(p1[1])
    det -= float(p1[0]) * float(p3[1]) + float(p2[0]) * float(p1[1]) + float(p3[0]) * float(p2[1])
    return det


def check_integer_sign(value: float | int) -> bool:
    """
    Checks if the given value is non-negative.

    :param value: The value to check.
    :return: True if the value is non-negative, False otherwise.
    """
    return value >= 0


def get_flows_segments(flows: list[SequenceFlow]) -> list[dict[str, dict[str, float]]]:
    """
    Extracts flow segments from the given flows.

    :param flows: A list of flows from the BPMN graph.
    :return: A list of flow segments with source and target points.
    """
    source_param_name = "source"
    target_param_name = "target"

    segments = []
    for flow in flows:
        waypoints = copy.deepcopy(flow.waypoints)
        source = waypoints.pop(0)
        while len(waypoints) > 0:
            target = waypoints.pop(0)
            segments.append({source_param_name: {consts.Consts.x: float(source[0]), consts.Consts.y: float(source[1])},
                             target_param_name: {consts.Consts.x: float(target[0]), consts.Consts.y: float(target[1])}})
            source = target
    return segments


def segments_common_points(segment_one: dict[str, dict[str, float]], segment_two: dict[str, dict[str, float]]) -> bool:
    """
    Checks if two segments share any common points.

    :param segment_one: The first segment.
    :param segment_two: The second segment.
    :return: True if the segments share common points, False otherwise.
    """
    source_param = "source"
    target_param = "target"
    return points_are_equal(segment_one[source_param], segment_two[source_param]) \
        or points_are_equal(segment_one[source_param], segment_two[target_param]) \
        or points_are_equal(segment_one[target_param], segment_two[source_param]) \
        or points_are_equal(segment_one[target_param], segment_two[target_param])


def points_are_equal(p1: dict[str, float], p2: dict[str, float]) -> bool:
    """
    Checks if two points are equal.

    :param p1: The first point as a dictionary with x and y coordinates.
    :param p2: The second point as a dictionary with x and y coordinates.
    :return: True if the points are equal, False otherwise.
    """
    return p1[consts.Consts.x] == p2[consts.Consts.x] and p1[consts.Consts.y] == p2[consts.Consts.y]


def do_intersect(segment_one: dict[str, dict[str, float]], segment_two: dict[str, dict[str, float]]) -> bool:
    """
    Determines if two segments intersect.

    :param segment_one: The first segment.
    :param segment_two: The second segment.
    :return: True if the segments intersect, False otherwise.
    """
    source_param = "source"
    target_param = "target"
    # Find the four orientations needed for general and special cases
    o1 = orientation(segment_one[source_param], segment_one[target_param], segment_two[source_param])
    o2 = orientation(segment_one[source_param], segment_one[target_param], segment_two[target_param])
    o3 = orientation(segment_two[source_param], segment_two[target_param], segment_one[source_param])
    o4 = orientation(segment_two[source_param], segment_two[target_param], segment_one[target_param])

    if o1 != o2 and o3 != o4:
        return True

    # Special Cases
    if o1 == 0 and lies_on_segment(segment_one[source_param], segment_one[target_param], segment_two[source_param]):
        return True

    if o2 == 0 and lies_on_segment(segment_one[source_param], segment_one[target_param], segment_two[target_param]):
        return True

    if o3 == 0 and lies_on_segment(segment_two[source_param], segment_two[target_param], segment_one[source_param]):
        return True

    if o4 == 0 and lies_on_segment(segment_two[source_param], segment_two[target_param], segment_one[target_param]):
        return True

    # Neither of special cases
    return False


def orientation(p1: dict[str, float], p2: dict[str, float], p3: dict[str, float]) -> int:
    """
    Determines the orientation of three points.

    :param p1: First point as a dictionary with x and y coordinates.
    :param p2: Second point as a dictionary with x and y coordinates.
    :param p3: Third point as a dictionary with x and y coordinates.
    :return: 0 if collinear, 1 if clockwise, 2 if counterclockwise.
    """
    val = (p2[consts.Consts.y] - p1[consts.Consts.y]) * (p3[consts.Consts.x] - p2[consts.Consts.x]) \
          - (p2[consts.Consts.x] - p1[consts.Consts.x]) * (p3[consts.Consts.y] - p2[consts.Consts.y])

    if val == 0:
        return 0  # collinear
    elif val > 0:
        return 1  # clockwise
    else:
        return 2  # counterclockwise


def lies_on_segment(p1: dict[str, float], p2: dict[str, float], p3: dict[str, float]) -> bool:
    """
    Checks if a point lies on a segment defined by two other points.

    :param p1: Start point of the segment.
    :param p2: End point of the segment.
    :param p3: The point to check.
    :return: True if the point lies on the segment, False otherwise.
    """
    return min(p1[consts.Consts.x], p2[consts.Consts.x]) <= p3[consts.Consts.x] \
        <= max(p1[consts.Consts.x], p2[consts.Consts.x]) \
        and min(p1[consts.Consts.y], p2[consts.Consts.y]) <= p3[consts.Consts.y] \
        <= max(p1[consts.Consts.y], p2[consts.Consts.y])


def count_segments(bpmn_graph: BpmnDiagramGraph) -> int:
    """
    Counts the number of segments in the BPMN graph.

    :param bpmn_graph: The BPMN graph object.
    :return: The number of segments.
    """
    flows = [flow for _, _, flow in bpmn_graph.get_flows()]
    segments = get_flows_segments(flows)
    return len(segments)


def compute_longest_path(bpmn_graph: BpmnDiagramGraph) -> tuple[list[FlowNode], int]:
    """
    Computes the longest path in the BPMN graph.

    :param bpmn_graph: The BPMN graph object.
    :return: A tuple containing the longest path and its length.
    """
    nodes = copy.deepcopy(bpmn_graph.get_nodes())
    no_incoming_flow_nodes = []
    for node in nodes:
        if len(node.incoming) == 0:
            no_incoming_flow_nodes.append(node)

    longest_path = []
    for node in no_incoming_flow_nodes:
        (output_path, output_path_len) = find_longest_path([], node, bpmn_graph)
        if output_path_len > len(longest_path):
            longest_path = output_path
    return longest_path, len(longest_path)


def find_longest_path(previous_nodes: list[FlowNode], node: FlowNode, bpmn_graph: BpmnDiagramGraph) -> tuple[
    list[FlowNode], int]:
    """
    Recursively finds the longest path starting from a given node.

    :param previous_nodes: List of nodes already visited.
    :param node: The current node.
    :param bpmn_graph: The BPMN graph object.
    :return: A tuple containing the longest path and its length.
    """
    outgoing_flows_list = node.outgoing
    longest_path = []

    tmp_previous_nodes = copy.deepcopy(previous_nodes)
    tmp_previous_nodes.append(node)

    if len(outgoing_flows_list) == 0:
        return tmp_previous_nodes, len(tmp_previous_nodes)

    for outgoing_flow_id in outgoing_flows_list:
        _, _, flow = bpmn_graph.get_flow_by_id(outgoing_flow_id)
        _, outgoing_node = bpmn_graph.get_node_by_id(flow.target_ref_id)
        if outgoing_node not in previous_nodes:
            (output_path, output_path_len) = find_longest_path(tmp_previous_nodes, outgoing_node, bpmn_graph)
            if output_path_len > len(longest_path):
                longest_path = output_path
    return longest_path, len(longest_path)


def compute_longest_path_tasks(bpmn_graph: BpmnDiagramGraph) -> tuple[list[FlowNode], int]:
    """
    Computes the longest path consisting of tasks in the BPMN graph.

    :param bpmn_graph: The BPMN graph object.
    :return: A tuple containing the longest path of tasks and its length.
    """

    nodes = copy.deepcopy(bpmn_graph.get_nodes())
    no_incoming_flow_nodes = []
    for node in nodes:
        if len(node.incoming) == 0:
            no_incoming_flow_nodes.append(node)

    longest_path = []
    for node in no_incoming_flow_nodes:
        (all_nodes, qualified_nodes) = find_longest_path_tasks([], [], node, bpmn_graph)
        if len(qualified_nodes) > len(longest_path):
            longest_path = qualified_nodes
    return longest_path, len(longest_path)


def find_longest_path_tasks(path: list[FlowNode], qualified_nodes: list[FlowNode], node: FlowNode,
                            bpmn_graph: BpmnDiagramGraph) -> tuple[list[FlowNode], list[FlowNode]]:
    """
    Recursively finds the longest path consisting of tasks starting from a given node.

    :param path: List of nodes already visited.
    :param qualified_nodes: List of task nodes in the current path.
    :param node: The current node.
    :param bpmn_graph: The BPMN graph object.
    :return: A tuple containing all nodes in the path and the task nodes in the path.
    """
    node_types = {NodeType.TASK, NodeType.SUB_PROCESS}
    outgoing_flows_list = node.outgoing

    if len(outgoing_flows_list) == 0:
        tmp_path = copy.deepcopy(path)
        tmp_path.append(node)
        tmp_qualified_nodes = copy.deepcopy(qualified_nodes)
        if node.node_type in node_types:
            tmp_qualified_nodes.append(node)
        return tmp_path, tmp_qualified_nodes
    else:
        longest_qualified_nodes = []
        longest_path = copy.deepcopy(path)
        longest_path.append(node)
        for outgoing_flow_id in outgoing_flows_list:
            _, _, flow = bpmn_graph.get_flow_by_id(outgoing_flow_id)
            _, outgoing_node = bpmn_graph.get_node_by_id(flow.target_ref_id)
            tmp_path = copy.deepcopy(path)
            tmp_path.append(node)
            tmp_qualified_nodes = copy.deepcopy(qualified_nodes)
            if node.node_type in node_types:
                tmp_qualified_nodes.append(node)

            if outgoing_node not in path:
                (path_all_nodes, path_qualified_nodes) = find_longest_path_tasks(tmp_path, tmp_qualified_nodes,
                                                                                 outgoing_node, bpmn_graph)
                if len(path_qualified_nodes) > len(longest_qualified_nodes):
                    longest_qualified_nodes = path_qualified_nodes
                    longest_path = path_all_nodes
            else:
                if len(tmp_qualified_nodes) > len(longest_qualified_nodes):
                    longest_qualified_nodes = tmp_qualified_nodes
                    longest_path = tmp_path
        return longest_path, longest_qualified_nodes
