# coding=utf-8
"""
Test unit, using simple graph made in BPMNEditor editor for import/export operation
"""
import unittest

import bpmn_python.bpmn_diagram_layouter as layouter
import bpmn_python.bpmn_diagram_rep as diagram
from bpmn_python.bpmn_diagram_export import BpmnDiagramGraphExport
from bpmn_python.graph.classes.flow_node import NodeType


class BPMNEditorTests(unittest.TestCase):
    """
    This class contains test for bpmn-python package functionality using an example BPMN diagram created in BPMNEditor.
    """
    output_directory = "./output/layouter/"

    def test_layouter_manually_created_diagram_simple_case(self) -> None:
        """
        Test for importing a simple BPMNEditor diagram example (as BPMN 2.0 XML) into inner representation
        and generating layout for it
        """
        output_file = "layouter_simple_case.xml"
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.create_new_diagram_graph(diagram_name="diagram1")
        process_id = bpmn_graph.add_process_to_diagram()
        [start_id, _] = bpmn_graph.add_modify_start_event_to_diagram(process_id, start_event_name="start_event")
        [task1_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="task1")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, start_id, task1_id, "start_to_one")

        [task2_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="task2")
        [end_id, _] = bpmn_graph.add_modify_end_event_to_diagram(process_id, end_event_name="end_event")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task1_id, task2_id, "one_to_two")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task2_id, end_id, "two_to_end")

        layouter.generate_layout(bpmn_graph)
        BpmnDiagramGraphExport.export_xml_file(self.output_directory, output_file, bpmn_graph)

    def test_layouter_manually_created_diagram_split_join_case(self) -> None:
        """
        Test for importing a simple BPMNEditor diagram example (as BPMN 2.0 XML) into inner representation
        and generating layout for it
        """
        output_file = "layouter_split_join_case.xml"
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.create_new_diagram_graph(diagram_name="diagram1")
        process_id = bpmn_graph.add_process_to_diagram()
        [start_id, _] = bpmn_graph.add_modify_start_event_to_diagram(process_id, start_event_name="start_event")
        [task1_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="task1")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, start_id, task1_id, "start_to_one")

        [exclusive_gate_fork_id, _] = bpmn_graph.add_modify_gateway_to_diagram(process_id,
                                                                        gateway_name="exclusive_gate_fork",
                                                                        gateway_type=NodeType.EXCLUSIVE)
        [task1_ex_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="task1_ex")
        [task2_ex_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="task2_ex")
        [exclusive_gate_join_id, _] = bpmn_graph.add_modify_gateway_to_diagram(process_id,
                                                                        gateway_name="exclusive_gate_join",
                                                                        gateway_type=NodeType.EXCLUSIVE)

        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task1_id, exclusive_gate_fork_id, "one_to_ex_fork")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, exclusive_gate_fork_id, task1_ex_id, "ex_fork_to_ex_one")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, exclusive_gate_fork_id, task2_ex_id, "ex_fork_to_ex_two")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task1_ex_id, exclusive_gate_join_id, "ex_one_to_ex_join")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task2_ex_id, exclusive_gate_join_id, "ex_two_to_ex_join")

        [task2_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="task2")
        [end_id, _] = bpmn_graph.add_modify_end_event_to_diagram(process_id, end_event_name="end_event")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, exclusive_gate_join_id, task2_id, "ex_join_to_two")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task2_id, end_id, "two_to_end")

        layouter.generate_layout(bpmn_graph)
        BpmnDiagramGraphExport.export_xml_file(self.output_directory, output_file, bpmn_graph)

    def test_layouter_manually_created_diagram_cycle_case(self) -> None:
        """
        Test for importing a simple BPMNEditor diagram example (as BPMN 2.0 XML) into inner representation
        and generating layout for it
        """
        output_file = "layouter_cycle_case.xml"
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.create_new_diagram_graph(diagram_name="diagram1")
        process_id = bpmn_graph.add_process_to_diagram()
        [start_id, _] = bpmn_graph.add_modify_start_event_to_diagram(process_id, start_event_name="start_event")
        [task1_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="task1")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, start_id, task1_id, "start_to_one")

        [exclusive_gate_fork_id, _] = bpmn_graph.add_modify_gateway_to_diagram(process_id,
                                                                        gateway_name="exclusive_gate_fork",
                                                                        gateway_type=NodeType.EXCLUSIVE)
        [task1_ex_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="task1_ex")
        [task2_ex_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="task2_ex")
        [exclusive_gate_join_id, _] = bpmn_graph.add_modify_gateway_to_diagram(process_id,
                                                                        gateway_name="exclusive_gate_join",
                                                                        gateway_type=NodeType.EXCLUSIVE)

        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task1_id, exclusive_gate_fork_id, "one_to_ex_fork")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, exclusive_gate_fork_id, task1_ex_id, "ex_fork_to_ex_one")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task2_ex_id, exclusive_gate_fork_id, "ex_two_to_ex_fork")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task1_ex_id, exclusive_gate_join_id, "ex_one_to_ex_join")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, exclusive_gate_join_id, task2_ex_id, "ex_join_to_ex_two")

        [task2_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="task2")
        [end_id, _] = bpmn_graph.add_modify_end_event_to_diagram(process_id, end_event_name="end_event")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, exclusive_gate_join_id, task2_id, "ex_join_to_two")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task2_id, end_id, "two_to_end")

        layouter.generate_layout(bpmn_graph)
        BpmnDiagramGraphExport.export_xml_file(self.output_directory, output_file, bpmn_graph)


if __name__ == '__main__':
    unittest.main()
