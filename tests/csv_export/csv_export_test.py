# coding=utf-8
"""
Unit tests for exporting process to CSV functionality.
"""

import os
import unittest

import bpmn_python.bpmn_diagram_rep as diagram
from bpmn_python.bpmn_diagram_export import BpmnDiagramGraphExport
from bpmn_python.bpmn_process_csv_export import BpmnDiagramGraphCsvExport
from bpmn_python.graph.classes.flow_node import NodeType
from bpmn_python.graph.classes.root_element.event_definition import EventDefinitionType


class CsvExportTests(unittest.TestCase):
    """
    This class contains test for manual diagram generation functionality.
    """
    output_directory = "./output/test-csv-export/"
    example_directory = "../examples/csv_export/"

    def test_csv_export_bank_account_example(self) -> None:
        # TODO not working correctly, problem with nested splits
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.load_diagram_from_xml_file(os.path.abspath(self.example_directory + "bank-account-process.bpmn"))
        BpmnDiagramGraphCsvExport.export_process_to_csv(bpmn_graph, self.output_directory, "bank-account-process.csv")

    def test_csv_export_checkin_process_example(self) -> None:
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.load_diagram_from_xml_file(os.path.abspath(self.example_directory + "checkin-process.bpmn"))
        BpmnDiagramGraphCsvExport.export_process_to_csv(bpmn_graph, self.output_directory, "checkin-process.csv")

    def test_csv_export_credit_process_example(self) -> None:
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.load_diagram_from_xml_file(os.path.abspath(self.example_directory + "credit-process.bpmn"))
        BpmnDiagramGraphCsvExport.export_process_to_csv(bpmn_graph, self.output_directory, "credit-process.csv")

    def test_csv_export_order_processing_example(self) -> None:
        # TODO not working correctly, problem with nested splits
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.load_diagram_from_xml_file(os.path.abspath(self.example_directory + "order-processing.bpmn"))
        BpmnDiagramGraphCsvExport.export_process_to_csv(bpmn_graph, self.output_directory, "order-processing.csv")

    def test_csv_export_pizza_order_example(self) -> None:
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.load_diagram_from_xml_file(os.path.abspath(self.example_directory + "pizza-order.bpmn"))
        BpmnDiagramGraphCsvExport.export_process_to_csv(bpmn_graph, self.output_directory, "pizza-order.csv")

    def test_csv_export_tram_process_example(self) -> None:
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.load_diagram_from_xml_file(os.path.abspath(self.example_directory + "tram-process.bpmn"))
        # TODO Problem with the loops
        #BpmnDiagramGraphCsvExport.export_process_to_csv(bpmn_graph, self.output_directory, "tram-process.csv")

    def test_csv_export_manual_simple_diagram(self) -> None:
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.create_new_diagram_graph(diagram_name="diagram1")
        process_id = bpmn_graph.add_process_to_diagram()
        [start_id, _] = bpmn_graph.add_modify_start_event_to_diagram(process_id, start_event_name="Start event",
                                                                     start_event_definition=EventDefinitionType.TIMER)
        [task1_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="Task 1")
        [subprocess1_id, _] = bpmn_graph.add_subprocess_to_diagram(process_id, subprocess_name="Subprocess 1")
        [subprocess2_id, _] = bpmn_graph.add_subprocess_to_diagram(process_id, subprocess_name="Subprocess 2")
        [task2_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="Task 2")
        [end_id, _] = bpmn_graph.add_modify_end_event_to_diagram(process_id, end_event_name="End event",
                                                                 end_event_definition=EventDefinitionType.MESSAGE)

        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, start_id, task1_id,
                                                sequence_flow_name="start_to_task_one")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task1_id, subprocess1_id,
                                                sequence_flow_name="task_one_to_subprocess_one")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, subprocess1_id, subprocess2_id,
                                                sequence_flow_name="subprocess_one_to_subprocess_two")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, subprocess2_id, task2_id,
                                                sequence_flow_name="subprocess_two_to_task_two")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task2_id, end_id,
                                                sequence_flow_name="task_two_to_end")

        BpmnDiagramGraphCsvExport.export_process_to_csv(bpmn_graph, self.output_directory, "simple_diagram.csv")
        BpmnDiagramGraphExport.export_xml_file(self.output_directory, "simple_diagram.bpmn", bpmn_graph)

    def test_csv_export_diagram_with_exclusive_parallel_gateway(self) -> None:
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.create_new_diagram_graph(diagram_name="diagram1")
        process_id = bpmn_graph.add_process_to_diagram()
        [start_id, _] = bpmn_graph.add_modify_start_event_to_diagram(process_id, start_event_name="Start event",
                                                                     start_event_definition=EventDefinitionType.TIMER)
        [task1_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="Task 1")

        [exclusive_gate_fork_id, _] = bpmn_graph.add_modify_gateway_to_diagram(process_id,
                                                                        gateway_name="Exclusive gate fork",
                                                                               gateway_type=NodeType.EXCLUSIVE)
        [task2_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="Task 2")
        [task3_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="Task 3")
        [task6_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="Task 6")
        [exclusive_gate_join_id, _] = bpmn_graph.add_modify_gateway_to_diagram(process_id,
                                                                        gateway_name="Exclusive gate join",
                                                                               gateway_type=NodeType.EXCLUSIVE)

        [parallel_gate_fork_id, _] = bpmn_graph.add_modify_gateway_to_diagram(process_id,
                                                                       gateway_name="Parallel gateway fork",
                                                                              gateway_type=NodeType.PARALLEL)
        [task4_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="Task 4")
        [task5_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="Task 5")
        [parallel_gate_join_id, _] = bpmn_graph.add_modify_gateway_to_diagram(process_id,
                                                                       gateway_name="Parallel gateway join",
                                                                              gateway_type=NodeType.PARALLEL)

        [end_id, _] = bpmn_graph.add_modify_end_event_to_diagram(process_id, end_event_name="End event",
                                                                 end_event_definition=EventDefinitionType.MESSAGE)

        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, start_id, task1_id,
                                                sequence_flow_name="Start to one")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task1_id, exclusive_gate_fork_id,
                                                sequence_flow_name="Task one to exclusive fork")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, exclusive_gate_fork_id, task2_id,
                                                sequence_flow_name="Exclusive fork to task two")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task2_id, task3_id,
                                                sequence_flow_name="Task two to task three")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, exclusive_gate_fork_id, parallel_gate_fork_id,
                                                sequence_flow_name="Exclusive fork to parallel fork")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, parallel_gate_fork_id, task4_id,
                                                sequence_flow_name="Parallel fork to task four")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, parallel_gate_fork_id, task5_id,
                                                sequence_flow_name="Parallel fork to task five")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task4_id, parallel_gate_join_id,
                                                sequence_flow_name="Task four to parallel join")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task5_id, parallel_gate_join_id,
                                                sequence_flow_name="Task five to parallel join")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, parallel_gate_join_id, task6_id,
                                                sequence_flow_name="Parallel join to task six")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task3_id, exclusive_gate_join_id,
                                                sequence_flow_name="Task three to exclusive join")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task6_id, exclusive_gate_join_id,
                                                sequence_flow_name="Task six to exclusive join")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, exclusive_gate_join_id, end_id,
                                                sequence_flow_name="Exclusive join to end event")

        BpmnDiagramGraphCsvExport.export_process_to_csv(bpmn_graph, self.output_directory, "exclusive_parallel_gateways_diagram.csv")
        BpmnDiagramGraphExport.export_xml_file(self.output_directory, "exclusive_parallel_gateways_diagram.bpmn",
                                               bpmn_graph)

    def test_csv_export_diagram_with_inclusive_parallel_gateway(self) -> None:
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.create_new_diagram_graph(diagram_name="diagram1")
        process_id = bpmn_graph.add_process_to_diagram()
        [start_id, _] = bpmn_graph.add_modify_start_event_to_diagram(process_id, start_event_name="Start event",
                                                                     start_event_definition=EventDefinitionType.TIMER)
        [task1_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="Task 1")

        [exclusive_gate_fork_id, _] = bpmn_graph.add_modify_gateway_to_diagram(process_id,
                                                                        gateway_name="Inclusive gate fork",
                                                                               gateway_type=NodeType.INCLUSIVE)
        [task2_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="Task 2")
        [task3_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="Task 3")
        [task6_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="Task 6")
        [exclusive_gate_join_id, _] = bpmn_graph.add_modify_gateway_to_diagram(process_id,
                                                                        gateway_name="Inclusive gate join",
                                                                               gateway_type=NodeType.INCLUSIVE)

        [parallel_gate_fork_id, _] = bpmn_graph.add_modify_gateway_to_diagram(process_id,
                                                                       gateway_name="Parallel gateway fork",
                                                                              gateway_type=NodeType.PARALLEL)
        [task4_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="Task 4")
        [task5_id, _] = bpmn_graph.add_modify_task_to_diagram(process_id, task_name="Task 5")
        [parallel_gate_join_id, _] = bpmn_graph.add_modify_gateway_to_diagram(process_id,
                                                                       gateway_name="Parallel gateway join",
                                                                              gateway_type=NodeType.PARALLEL)

        [end_id, _] = bpmn_graph.add_modify_end_event_to_diagram(process_id, end_event_name="End event",
                                                                 end_event_definition=EventDefinitionType.MESSAGE)

        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, start_id, task1_id,
                                                sequence_flow_name="Start to one")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task1_id, exclusive_gate_fork_id,
                                                sequence_flow_name="Task one to exclusive fork")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, exclusive_gate_fork_id, task2_id,
                                                sequence_flow_name="Condition: approved")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task2_id, task3_id,
                                                sequence_flow_name="Task two to task three")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, exclusive_gate_fork_id, parallel_gate_fork_id,
                                                sequence_flow_name="Condition: rejected")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, parallel_gate_fork_id, task4_id,
                                                sequence_flow_name="Parallel fork to task four")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, parallel_gate_fork_id, task5_id,
                                                sequence_flow_name="Parallel fork to task five")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task4_id, parallel_gate_join_id,
                                                sequence_flow_name="Task four to parallel join")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task5_id, parallel_gate_join_id,
                                                sequence_flow_name="Task five to parallel join")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, parallel_gate_join_id, task6_id,
                                                sequence_flow_name="Parallel join to task six")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task3_id, exclusive_gate_join_id,
                                                sequence_flow_name="Task three to exclusive join")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, task6_id, exclusive_gate_join_id,
                                                sequence_flow_name="Task six to exclusive join")
        bpmn_graph.add_modify_sequence_flow_to_diagram(process_id, exclusive_gate_join_id, end_id,
                                                sequence_flow_name="Exclusive join to end event")

        BpmnDiagramGraphCsvExport.export_process_to_csv(bpmn_graph, self.output_directory, "inclusive_parallel_gateways_diagram.csv")
        BpmnDiagramGraphExport.export_xml_file(self.output_directory, "inclusive_parallel_gateways_diagram.bpmn",
                                               bpmn_graph)


if __name__ == '__main__':
    unittest.main()
