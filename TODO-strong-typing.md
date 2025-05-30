### Old representation of graph:

```
self.diagram_graph = nx.Graph()
self.sequence_flows = {}
self.process_elements = {}
self.diagram_attributes = {}
self.plane_attributes = {}
self.collaboration = {}
```

### Comparison with new model:

self.diagram_graph - node (== FlowNode? and its child elements), edge == SequenceFlow

self.sequence_flows - edges == Dict[ID, SequenceFlow]

self.process_elements - == Dict[ID, Process]

self.diagram_attributes - == probably Dict[str, str], not sure yet

self.plane_attributes - == probably Dict[str, str], not sure yet

self.collaboration - messageFlows == Dict[ID, MessageFlow], participants == Dict[ID, Participant]

we will also add self.nodes since we need to keep track of the nodes in the graph _alongside_ the nx.Graph object.

### New representation of graph (WIP):

```
nodes: Dict[ID, FlowNode]
sequence_flows: Dict[ID, SequenceFlow]
process_elements: Dict[ID, Process]
diagram_attributes: Dict[str, str]
plane_attributes: Dict[str, str]
message_flows: Dict[ID, MessageFlow]
participants: Dict[ID, Participant]
```

TODOs:
- [x] **node_type** property for FlowNode class?
- [x] **event_definitions**? look up consts.Consts.event_definitions
- [x] **node_creator** for all gateway types
- [ ] **create_new_diagram_graph** make sure that it initializes new diagram properly
- [ ] **attached_to_ref** in import
- [ ] **event_definition_type** add all possible types
- [ ]
