# coding=utf-8
"""
Test unit, using simple graph made in BPMNEditor editor for import/export operation
"""
import os
import unittest

import bpmn_python.bpmn_diagram_rep as diagram
import bpmn_python.bpmn_diagram_visualizer as visualizer
from bpmn_python.bpmn_diagram_export import BpmnDiagramGraphExport


class BPMNEditorTests(unittest.TestCase):
    """
    This class contains test for bpmn-python package functionality using an example BPMN diagram created in BPMNEditor.
    """
    output_directory = "./output/test-bpmneditor/"
    example_path = "../examples/xml_import_export/bpmn_editor_simple_example.xml"
    output_file_with_di = "BPMNEditor-example-output.xml"
    output_file_no_di = "BPMNEditor-example-output-no-di.xml"
    output_dot_file = "BPMNEditor-example"
    output_png_file = "BPMNEditor-example"
    output_dot_auto_layout_file = "BPMNEditor-example-auto-layout"
    output_png_auto_layout_file = "BPMNEditor-example-auto-layout"

    def test_loadBPMNEditorDiagram(self) -> None:
        """
        Test for importing a simple BPMNEditor diagram example (as BPMN 2.0 XML) into inner representation
        and later exporting it to XML file
        """
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.load_diagram_from_xml_file(os.path.abspath(self.example_path))
        BpmnDiagramGraphExport.export_xml_file(self.output_directory, self.output_file_with_di, bpmn_graph)
        BpmnDiagramGraphExport.export_xml_file_no_di(self.output_directory, self.output_file_no_di, bpmn_graph)

    def test_loadBPMNEditorDiagramAndVisualize(self) -> None:
        """
        Test for importing a simple BPMNEditor diagram example (as BPMN 2.0 XML) into inner representation
        and later exporting it to XML file. Includes test for visualization functionality.
        """
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.load_diagram_from_xml_file(os.path.abspath(self.example_path))
        # Uncomment line below to get a simple view of created diagram
        # visualizer.visualize_diagram(bpmn_graph)
        visualizer.bpmn_diagram_to_dot_file(bpmn_graph, self.output_directory + self.output_dot_file)
        visualizer.bpmn_diagram_to_png(bpmn_graph, self.output_directory + self.output_png_file)

        visualizer.bpmn_diagram_to_dot_file(bpmn_graph, self.output_directory + self.output_dot_auto_layout_file,
                                            auto_layout=True)
        visualizer.bpmn_diagram_to_png(bpmn_graph, self.output_directory + self.output_png_auto_layout_file,
                                       auto_layout=True)

        BpmnDiagramGraphExport.export_xml_file(self.output_directory, self.output_file_with_di, bpmn_graph)
        BpmnDiagramGraphExport.export_xml_file_no_di(self.output_directory, self.output_file_no_di, bpmn_graph)


if __name__ == '__main__':
    unittest.main()
