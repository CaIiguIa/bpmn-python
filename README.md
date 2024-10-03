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

## TO DO

- [ ] Fix dot file export
- [ ] Tests for diagram rep
- [ ] Change all consts to enums