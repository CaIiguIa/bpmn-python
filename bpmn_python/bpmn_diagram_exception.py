# coding=utf-8
"""
Custom exception class for bpmn_python
"""


class BpmnPythonError(Exception):
    """
    Custom BpmnPythonError exception
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class BpmnNodeTypeError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class BpmnNodeNotFoundError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class BpmnFlowNotFoundError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BpmnConnectedFlowsError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)