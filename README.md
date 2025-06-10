# bpmn-python
Project for creating a Python library that allows to import/export BPMN diagram (as an XML file) and provides a simple visualization capabilities

Project structure
* bpmn_python - main module of project, includes all source code
* tests - unit tests for package
* examples - examples of XML files used in tests
* docs - documentation for package


## Development
```bash
poetry install
```

Run tests with HTML coverage report:
```bash
poetry run pytest
```

## Port guide

We tried to avoid big changes to the interface of the library, but _some_ changes were necessary. Below is a list of
changes that may affect your code.

- some methods that previously required node type as string value as an argument now require enum value instead
- some main class's methods that handled all sorts of import or export functionality were removed. Import and export
  functionalities can be found in those classes:
  - `BpmnDiagramGraphExport`
  - `BpmnDiagramGraphImport`
  - `BpmnDiagramGraphCsvExport`
  - `BpmnDiagramGraphCSVImport`
- some methods that previously required graph objects in their old representation (nested dicts) as an argument now
  require their class representation

### Changes to data model

#### BpmnDiagramGraph.diagram_graph

- Previously stored nodes and edges
- This field was removed. nx.Graph for the BpmnDiagramGraph can be generated using the
  `BpmnDiagramGraph.get_diagram_graph()` method. This graph is completely separated from the data model. **Changes to
  the data model will not affect the graph, and vice versa.**
- The same information is now stored in attributes:
  - `BpmnDiagramGraph.nodes`
  - `BpmnDiagramGraph.sequence_flows`

#### BpmnDiagramGraph.sequence_flows

- Type was changed to `Dict[str, SequenceFlow]`

#### BpmnDiagramGraph.process_elements

- Type was changed to `Dict[str, Process]`

#### BpmnDiagramGraph.diagram_attributes

- Unchanged

#### BpmnDiagramGraph.plane_attributes

- Unchanged

#### BpmnDiagramGraph.collaboration

- Split into three attributes:
  - `BpmnDiagramGraph.message_flows`
  - `BpmnDiagramGraph.participants`
  - `BpmnDiagramGraph.collaboration_id`
