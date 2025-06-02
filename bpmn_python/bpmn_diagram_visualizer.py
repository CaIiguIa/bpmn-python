# coding=utf-8
"""
BPMN diagram visualization methods
"""
import matplotlib.pyplot as plt
import networkx as nx
import pydotplus
import bpmn_python.bpmn_python_consts as consts
from bpmn_python.bpmn_diagram_rep import BpmnDiagramGraph
from networkx.drawing.nx_pydot import write_dot


def visualize_diagram(bpmn_diagram: BpmnDiagramGraph):
    """
    Shows a simple visualization of diagram

    :param bpmn_diagram: an instance of BPMNDiagramGraph class.
    """
    g = bpmn_diagram.get_diagram_graph()
    # if g is None:
    #     raise ValueError("BPMN diagram graph is not set. Please use 'create_diagram_graph' method first.")
    pos = bpmn_diagram.get_nodes_positions()
    nx.draw_networkx_nodes(g, pos, node_shape='s', node_color='white',
                           nodelist=bpmn_diagram.get_nodes_id_list_by_type(consts.Consts.task))
    nx.draw_networkx_nodes(g, pos, node_shape='s', node_color='white',
                           nodelist=bpmn_diagram.get_nodes_id_list_by_type(consts.Consts.subprocess))
    nx.draw_networkx_nodes(g, pos, node_shape='d', node_color='white',
                           nodelist=bpmn_diagram.get_nodes_id_list_by_type(consts.Consts.complex_gateway))
    nx.draw_networkx_nodes(g, pos, node_shape='o', node_color='white',
                           nodelist=bpmn_diagram.get_nodes_id_list_by_type(consts.Consts.event_based_gateway))
    nx.draw_networkx_nodes(g, pos, node_shape='d', node_color='white',
                           nodelist=bpmn_diagram.get_nodes_id_list_by_type(consts.Consts.inclusive_gateway))
    nx.draw_networkx_nodes(g, pos, node_shape='d', node_color='white',
                           nodelist=bpmn_diagram.get_nodes_id_list_by_type(consts.Consts.exclusive_gateway))
    nx.draw_networkx_nodes(g, pos, node_shape='d', node_color='white',
                           nodelist=bpmn_diagram.get_nodes_id_list_by_type(consts.Consts.parallel_gateway))
    nx.draw_networkx_nodes(g, pos, node_shape='o', node_color='white',
                           nodelist=bpmn_diagram.get_nodes_id_list_by_type(consts.Consts.start_event))
    nx.draw_networkx_nodes(g, pos, node_shape='o', node_color='white',
                           nodelist=bpmn_diagram.get_nodes_id_list_by_type(consts.Consts.intermediate_catch_event))
    nx.draw_networkx_nodes(g, pos, node_shape='o', node_color='white',
                           nodelist=bpmn_diagram.get_nodes_id_list_by_type(consts.Consts.end_event))
    nx.draw_networkx_nodes(g, pos, node_shape='o', node_color='white',
                           nodelist=bpmn_diagram.get_nodes_id_list_by_type(consts.Consts.intermediate_throw_event))

    node_labels = {}
    for node in g.nodes(data=True):
        node_labels[node[0]] = node[1].get(consts.Consts.node_name)
    nx.draw_networkx_labels(g, pos, node_labels)

    nx.draw_networkx_edges(g, pos)

    edge_labels = {}
    for edge in g.edges(data=True):
        edge_labels[(edge[0], edge[1])] = edge[2].get(consts.Consts.name)
    nx.draw_networkx_edge_labels(g, pos, edge_labels)

    plt.show()


def bpmn_diagram_to_dot_file(bpmn_diagram: BpmnDiagramGraph, file_name: str, auto_layout=False):
    """
    Convert diagram graph to dot file

    :param bpmn_diagram: an instance of BPMNDiagramGraph class,
    :param file_name: name of generated file.
    :param auto_layout: whether to re-layout the graph.
    """
    if auto_layout:
        graph = _auto_layout_diagram(bpmn_diagram)
        graph.write(file_name + ".dot", format='dot')
    else:
        g = bpmn_diagram.get_diagram_graph()
        write_dot(g, file_name + ".dot")

def bpmn_diagram_to_png(bpmn_diagram: BpmnDiagramGraph, file_name: str, auto_layout=False):
    """
    Create a png picture for given diagram

    :param bpmn_diagram: an instance of BPMNDiagramGraph class,
    :param file_name: name of generated file.
    :param auto_layout: whether to re-layout the graph.
    """
    if auto_layout:
        graph = _auto_layout_diagram(bpmn_diagram)
        graph.write(file_name + ".png", format='png')
    else:
        g = bpmn_diagram.get_diagram_graph()
        nx.draw(g, with_labels=True)
        plt.savefig(file_name + ".png")
        plt.clf()

def _auto_layout_diagram(bpmn_diagram: BpmnDiagramGraph):
    g = bpmn_diagram.get_diagram_graph()
    graph = pydotplus.Dot()

    for node in g.nodes(data=True):

        if node[1].get(consts.Consts.type) == consts.Consts.task:
            n = pydotplus.Node(name=node[0], shape="box", style="rounded", label=node[1].get(consts.Consts.id))
        elif node[1].get(consts.Consts.type) == consts.Consts.exclusive_gateway:
            n = pydotplus.Node(name=node[0], shape="diamond", label=node[1].get(consts.Consts.id))
        else:
            n = pydotplus.Node(name=node[0], label=node[1].get(consts.Consts.id))
        graph.add_node(n)

    for edge in g.edges(data=True):
        e = pydotplus.Edge(src=edge[2].get(consts.Consts.source_ref),
                           dst=edge[2].get(consts.Consts.target_ref),
                           label=edge[2].get(consts.Consts.name))
        graph.add_edge(e)

    return graph
