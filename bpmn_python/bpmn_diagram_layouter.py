# coding=utf-8
"""
Package with BPMNDiagramGraph - graph representation of BPMN diagram
"""
import copy

import bpmn_python.bpmn_python_consts as consts
import bpmn_python.grid_cell_class as cell_class


def generate_layout(bpmn_graph):
    """
    Generates a layout for the BPMN diagram.

    This function performs the following steps:
    1. Classifies elements in the BPMN graph.
    2. Performs a topological sort of the graph.
    3. Creates a grid layout for the nodes.
    4. Sets coordinates for the nodes.
    5. Sets waypoints for the flows.

    :param bpmn_graph: An instance of BPMNDiagramGraph class.
    """
    classification = generate_elements_clasification(bpmn_graph)
    (sorted_nodes_with_classification, backward_flows) = topological_sort(bpmn_graph, classification[0])
    grid = grid_layout(bpmn_graph, sorted_nodes_with_classification)
    set_coordinates_for_nodes(bpmn_graph, grid)
    set_flows_waypoints(bpmn_graph)


def generate_elements_clasification(bpmn_graph):
    """
    Generates a classification of elements in the BPMN graph.

    This function classifies nodes and flows in the BPMN graph based on their type and properties.
    Nodes are classified into categories such as "Element", "Join", "Split", "Start Event", and "End Event".
    Flows are classified as "Flow".

    :param bpmn_graph: An instance of BPMNDiagramGraph representing the BPMN diagram.
    :return: A tuple containing two lists:
             - nodes_classification: A list of dictionaries where each dictionary represents a node and its classification.
             - flows_classification: A list of dictionaries where each dictionary represents a flow and its classification.
    """
    nodes_classification = []
    node_param_name = "node"
    flow_param_name = "flow"
    classification_param_name = "classification"

    classification_element = "Element"
    classification_join = "Join"
    classification_split = "Split"
    classification_start_event = "Start Event"
    classification_end_event = "End Event"

    task_list = bpmn_graph.get_nodes(consts.Consts.task)
    for element in task_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element, classification_param_name: tmp}]

    subprocess_list = bpmn_graph.get_nodes(consts.Consts.subprocess)
    for element in subprocess_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element, classification_param_name: tmp}]

    complex_gateway_list = bpmn_graph.get_nodes(consts.Consts.complex_gateway)
    for element in complex_gateway_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element, classification_param_name: tmp}]

    event_based_gateway_list = bpmn_graph.get_nodes(consts.Consts.event_based_gateway)
    for element in event_based_gateway_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element, classification_param_name: tmp}]

    inclusive_gateway_list = bpmn_graph.get_nodes(consts.Consts.inclusive_gateway)
    for element in inclusive_gateway_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element, classification_param_name: tmp}]

    exclusive_gateway_list = bpmn_graph.get_nodes(consts.Consts.exclusive_gateway)
    for element in exclusive_gateway_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element, classification_param_name: tmp}]

    parallel_gateway_list = bpmn_graph.get_nodes(consts.Consts.parallel_gateway)
    for element in parallel_gateway_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element, classification_param_name: tmp}]

    start_event_list = bpmn_graph.get_nodes(consts.Consts.start_event)
    for element in start_event_list:
        tmp = [classification_element, classification_start_event]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element, classification_param_name: tmp}]

    intermediate_catch_event_list = bpmn_graph.get_nodes(consts.Consts.intermediate_catch_event)
    for element in intermediate_catch_event_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element, classification_param_name: tmp}]

    end_event_list = bpmn_graph.get_nodes(consts.Consts.end_event)
    for element in end_event_list:
        tmp = [classification_element, classification_end_event]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element, classification_param_name: tmp}]

    intermediate_throw_event_list = bpmn_graph.get_nodes(consts.Consts.intermediate_throw_event)
    for element in intermediate_throw_event_list:
        tmp = [classification_element]
        if len(element[1][consts.Consts.incoming_flow]) >= 2:
            tmp.append(classification_join)
        if len(element[1][consts.Consts.outgoing_flow]) >= 2:
            tmp.append(classification_split)
        nodes_classification += [{node_param_name: element, classification_param_name: tmp}]

    flows_classification = []
    flows_list = bpmn_graph.get_flows()
    for flow in flows_list:
        flows_classification += [{flow_param_name: flow, classification_param_name: ["Flow"]}]

    return nodes_classification, flows_classification


def topological_sort(bpmn_graph, nodes_with_classification):
    """
    Performs a topological sort on the BPMN graph.

    This function sorts the nodes in the BPMN graph in topological order and identifies backward flows.

    :param bpmn_graph: An instance of BPMNDiagramGraph representing the BPMN diagram.
    :param nodes_with_classification: A list of nodes with their classifications.
    :return: A tuple containing:
             - sorted_nodes_with_classification: A list of nodes sorted in topological order.
             - backward_flows: A list of flows that represent backward edges in the graph.
    """
    node_param_name = "node"
    classification_param_name = "classification"

    tmp_nodes_with_classification = copy.deepcopy(nodes_with_classification)
    sorted_nodes_with_classification = []
    no_incoming_flow_nodes = []
    backward_flows = []

    while tmp_nodes_with_classification:
        for node_with_classification in tmp_nodes_with_classification:
            incoming_list = node_with_classification[node_param_name][1][consts.Consts.incoming_flow]
            if len(incoming_list) == 0:
                no_incoming_flow_nodes.append(node_with_classification)
        if len(no_incoming_flow_nodes) > 0:
            while len(no_incoming_flow_nodes) > 0:
                node_with_classification = no_incoming_flow_nodes.pop()
                tmp_nodes_with_classification.remove(node_with_classification)
                sorted_nodes_with_classification \
                    .append(next(tmp_node for tmp_node in nodes_with_classification
                                 if tmp_node[node_param_name][0] == node_with_classification[node_param_name][0]))

                outgoing_list = list(node_with_classification[node_param_name][1][consts.Consts.outgoing_flow])
                tmp_outgoing_list = list(outgoing_list)

                for flow_id in tmp_outgoing_list:
                    '''
                    - Remove the outgoing flow for source flow node (the one without incoming flows)
                    - Get the target node
                    - Remove the incoming flow for target flow node
                    '''
                    outgoing_list.remove(flow_id)
                    node_with_classification[node_param_name][1][consts.Consts.outgoing_flow].remove(flow_id)

                    flow = bpmn_graph.get_flow_by_id(flow_id)
                    target_id = flow[2][consts.Consts.target_ref]
                    target = next(tmp_node[node_param_name]
                                  for tmp_node in tmp_nodes_with_classification
                                  if tmp_node[node_param_name][0] == target_id)
                    target[1][consts.Consts.incoming_flow].remove(flow_id)
        else:
            for node_with_classification in tmp_nodes_with_classification:
                if "Join" in node_with_classification[classification_param_name]:
                    incoming_list = list(node_with_classification[node_param_name][1][consts.Consts.incoming_flow])
                    tmp_incoming_list = list(incoming_list)
                    for flow_id in tmp_incoming_list:
                        incoming_list.remove(flow_id)

                        flow = bpmn_graph.get_flow_by_id(flow_id)

                        source_id = flow[2][consts.Consts.source_ref]
                        source = next(tmp_node[node_param_name]
                                      for tmp_node in tmp_nodes_with_classification
                                      if tmp_node[node_param_name][0] == source_id)
                        source[1][consts.Consts.outgoing_flow].remove(flow_id)

                        target_id = flow[2][consts.Consts.target_ref]
                        target = next(tmp_node[node_param_name]
                                      for tmp_node in tmp_nodes_with_classification
                                      if tmp_node[node_param_name][0] == target_id)
                        target[1][consts.Consts.incoming_flow].remove(flow_id)
                        backward_flows.append(flow)
    return sorted_nodes_with_classification, backward_flows


def grid_layout(bpmn_graph, sorted_nodes_with_classification):
    """
    Creates a grid layout for the BPMN diagram.

    This function places nodes in a grid based on their topological order and classifications.

    :param bpmn_graph: An instance of BPMNDiagramGraph representing the BPMN diagram.
    :param sorted_nodes_with_classification: A list of nodes sorted in topological order with their classifications.
    :return: A grid layout as a list of GridCell objects.
    """
    tmp_nodes_with_classification = list(sorted_nodes_with_classification)

    last_row = consts.Consts.grid_column_width
    last_col = 1
    grid = []
    while tmp_nodes_with_classification:
        node_with_classification = tmp_nodes_with_classification.pop(0)
        (grid, last_row, last_col) = place_element_in_grid(node_with_classification, grid, last_row, last_col,
                                                           bpmn_graph, tmp_nodes_with_classification)
    return grid


def place_element_in_grid(node_with_classification, grid, last_row, last_col, bpmn_graph, nodes_with_classification,
                          enforced_row_num=None):
    """
    Places a node in the grid.

    This function determines the position of a node in the grid based on its predecessors and successors.

    :param node_with_classification: A dictionary representing the node and its classification.
    :param grid: The current grid layout as a list of GridCell objects.
    :param last_row: The last row number used in the grid.
    :param last_col: The last column number used in the grid.
    :param bpmn_graph: An instance of BPMNDiagramGraph representing the BPMN diagram.
    :param nodes_with_classification: A list of nodes with their classifications.
    :param enforced_row_num: An optional row number to enforce for the node.
    :return: A tuple containing:
             - grid: The updated grid layout.
             - last_row: The updated last row number.
             - last_col: The updated last column number.
    """
    node_param_name = "node"
    classification_param_name = "classification"

    node_id = node_with_classification[node_param_name][0]
    incoming_flows = node_with_classification[node_param_name][1][consts.Consts.incoming_flow]
    outgoing_flows = node_with_classification[node_param_name][1][consts.Consts.outgoing_flow]

    if len(incoming_flows) == 0:
        # if node has no incoming flow, put it in new row
        current_element_row = last_row
        current_element_col = last_col
        if enforced_row_num:
            insert_into_grid(grid, enforced_row_num, current_element_col, node_id)
        else:
            insert_into_grid(grid, current_element_row, current_element_col, node_id)
        last_row += consts.Consts.grid_column_width
    elif "Join" not in node_with_classification[classification_param_name]:
        # if node is not a Join, put it right from its predecessor (element should only have one predecessor)
        flow_id = incoming_flows[0]
        flow = bpmn_graph.get_flow_by_id(flow_id)
        predecessor_id = flow[2][consts.Consts.source_ref]
        predecessor_cell = next(grid_cell for grid_cell in grid if grid_cell.node_id == predecessor_id)
        # insert into cell right from predecessor - no need to insert new column or row
        current_element_col = predecessor_cell.col + 1
        current_element_row = predecessor_cell.row
        if enforced_row_num is not None:
            insert_into_grid(grid, enforced_row_num, current_element_col, node_id)
        else:
            insert_into_grid(grid, current_element_row, current_element_col, node_id)
    # TODO consider rule for split/join node
    else:
        # find the rightmost predecessor - put into next column
        # if last_split was passed, use row number from it, otherwise compute mean from predecessors
        predecessors_id_list = []
        for flow_id in incoming_flows:
            flow = bpmn_graph.get_flow_by_id(flow_id)
            predecessors_id_list.append(flow[2][consts.Consts.source_ref])

        max_col_num = 0
        row_num_sum = 0
        # TODO try to implement corresponding split finding
        for grid_cell in grid:
            if grid_cell.node_id in predecessors_id_list:
                row_num_sum += grid_cell.row
                if grid_cell.col > max_col_num:
                    max_col_num = grid_cell.col
        current_element_row = row_num_sum // len(predecessors_id_list)
        current_element_col = max_col_num + 1
        if enforced_row_num:
            insert_into_grid(grid, enforced_row_num, current_element_col, node_id)
        else:
            insert_into_grid(grid, current_element_row, current_element_col, node_id)

    if "Split" in node_with_classification[classification_param_name]:
        successors_id_list = []
        for flow_id in outgoing_flows:
            flow = bpmn_graph.get_flow_by_id(flow_id)
            successors_id_list.append(flow[2][consts.Consts.target_ref])
        num_of_successors = len(successors_id_list)
        successor_node_list = [successor_node for successor_node in nodes_with_classification
                                      if successor_node[node_param_name][0] in successors_id_list]

        if num_of_successors % 2 != 0:
            # if number of successors is even, put one half over the split, second half below
            # proceed with first half
            centre = (num_of_successors // 2)
            for index in range(0, centre):
                # place element above split
                successor_node = successor_node_list[index]
                (grid, last_row, last_col) = place_element_in_grid(successor_node, grid, last_row, last_col,
                                                                   bpmn_graph,nodes_with_classification, current_element_row + ((index + 1) * consts.Consts.grid_column_width))

                nodes_with_classification.remove(successor_node)

            successor_node = successor_node_list[centre]
            (grid, last_row, last_col) = place_element_in_grid(successor_node, grid, last_row, last_col,
                                                               bpmn_graph,nodes_with_classification, current_element_row)
            nodes_with_classification.remove(successor_node)
            for index in range(centre + 1, num_of_successors):
                # place element below split
                successor_node = successor_node_list[index]
                (grid, last_row, last_col) = place_element_in_grid(successor_node, grid, last_row, last_col,
                                                                   bpmn_graph,nodes_with_classification, current_element_row - ((index - centre) * consts.Consts.grid_column_width))

                nodes_with_classification.remove(successor_node)
        else:
            centre = (num_of_successors // 2)
            for index in range(0, centre):
                # place element above split
                successor_node = successor_node_list[index]
                (grid, last_row, last_col) = place_element_in_grid(successor_node, grid, last_row, last_col,
                                                                   bpmn_graph,nodes_with_classification, current_element_row + (index + 1) * consts.Consts.grid_column_width)

                nodes_with_classification.remove(successor_node)


            for index in range(centre, num_of_successors):
                # place element below split
                successor_node = successor_node_list[index]
                (grid, last_row, last_col) = place_element_in_grid(successor_node, grid, last_row, last_col,
                                                                   bpmn_graph,nodes_with_classification, current_element_row - ((index - centre + 1) * consts.Consts.grid_column_width))

                nodes_with_classification.remove(successor_node)


    return grid, last_row, last_col


def insert_into_grid(grid, row, col, node_id):
    """
    Inserts a node into the grid.

    This function places a node in the specified row and column of the grid. If the cell is already occupied,
    it shifts rows below the specified row.

    :param grid: The current grid layout as a list of GridCell objects.
    :param row: The row number where the node should be placed.
    :param col: The column number where the node should be placed.
    :param node_id: The ID of the node to be placed.
    """
    # if row <= 0:
    #     row = 1
    occupied_cell = None
    try:
        occupied_cell = next(grid_cell for grid_cell in grid if grid_cell.row == row and grid_cell.col == col)
    except StopIteration:
        pass
    # if cell is already occupied, insert new row
    if occupied_cell:
        for grid_cell in grid:
            if grid_cell.row >= row:
                grid_cell.row += consts.Consts.width
    grid.append(cell_class.GridCell(row, col, node_id))


def set_coordinates_for_nodes(bpmn_graph, grid):
    """
    Sets the coordinates for nodes in the BPMN diagram.

    This function assigns x and y coordinates to each node based on its position in the grid.

    :param bpmn_graph: An instance of BPMNDiagramGraph representing the BPMN diagram.
    :param grid: The grid layout as a list of GridCell objects.
    """

    nodes = bpmn_graph.get_nodes()
    for node in nodes:
        cell = next(grid_cell for grid_cell in grid if grid_cell.node_id == node[0])
        node[1][consts.Consts.x] = str(cell.col * 150 + 50)
        node[1][consts.Consts.y] = str(cell.row * 100 + 50)


def set_flows_waypoints(bpmn_graph):
    """
    Sets waypoints for flows in the BPMN diagram.

    This function calculates and assigns waypoints for each flow based on the positions of its source and target nodes.

    :param bpmn_graph: An instance of BPMNDiagramGraph representing the BPMN diagram.
    """
    # TODO hardcoded node center, better compute it with x,y coordinates and height/width
    # TODO get rid of string cast
    flows = bpmn_graph.get_flows()
    for flow in flows:
        source_node = bpmn_graph.get_node_by_id(flow[2][consts.Consts.source_ref])
        target_node = bpmn_graph.get_node_by_id(flow[2][consts.Consts.target_ref])
        source_type = source_node[1][consts.Consts.type]
        target_type = target_node[1][consts.Consts.type]
        if source_type == consts.Consts.parallel_gateway or source_type == consts.Consts.inclusive_gateway or source_type == consts.Consts.exclusive_gateway:
            flow[2][consts.Consts.waypoints] = [(str(int(source_node[1][consts.Consts.x]) + 50),
                                                 str(int(source_node[1][consts.Consts.y]) + 50)),
                                                (str(int(source_node[1][consts.Consts.x]) + 50),
                                                 str(int(target_node[1][consts.Consts.y]) + 50)),
                                                (str(int(target_node[1][consts.Consts.x])),
                                                 str(int(target_node[1][consts.Consts.y]) + 50))]
        elif source_node[1][consts.Consts.y] == target_node[1][consts.Consts.y]:
            flow[2][consts.Consts.waypoints] = [(str(int(source_node[1][consts.Consts.x]) + 50),
                                                 str(int(source_node[1][consts.Consts.y]) + 50)),
                                                (str(int(target_node[1][consts.Consts.x])),
                                                 str(int(target_node[1][consts.Consts.y]) + 50))]

        elif target_type == consts.Consts.parallel_gateway or target_type == consts.Consts.inclusive_gateway or target_type == consts.Consts.exclusive_gateway:
            flow[2][consts.Consts.waypoints] = [(str(int(source_node[1][consts.Consts.x]) + 50),
                                                 str(int(source_node[1][consts.Consts.y]) + 50)),
                                                (str(int(target_node[1][consts.Consts.x]) + 50),
                                                 str(int(source_node[1][consts.Consts.y]) + 50)),
                                                (str(int(target_node[1][consts.Consts.x]) + 50),
                                                 str(int(target_node[1][consts.Consts.y])))]
        else:
            flow[2][consts.Consts.waypoints] = [(str(int(source_node[1][consts.Consts.x]) + 50),
                                                 str(int(source_node[1][consts.Consts.y]) + 50)),
                                                (str(int(target_node[1][consts.Consts.x])),
                                                 str(int(target_node[1][consts.Consts.y]) + 50))]
