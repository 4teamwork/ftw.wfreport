from Products.DCWorkflow.interfaces import IDCWorkflowDefinition
from ftw.wfreport.interfaces import IWorkflowReportConfig
from zope.component import adapts
from zope.i18n import translate
from zope.interface import implements



class DefaultWorkflowConfig(object):

    implements(IWorkflowReportConfig)
    adapts(IDCWorkflowDefinition)

    def __init__(self, workflow):
        self.workflow = workflow

    def get_hidden_permissions(self):
        return ['Access contents information',
                ]

    def get_merged_permissions(self):
        return []

    def get_merged_permissions_mapped_by_permission(self):
        mapped = {}
        for merge in self.get_merged_permissions():
            for permission in merge.get('permissions'):
                mapped[permission] = merge

        return mapped

    def order_states(self, states):
        new_states = []
        for state in states:
            if state.initial:
                new_states.insert(0, state)
            else:
                new_states.append(state)

        return new_states

    def order_states_by_ids(self, states, state_ids):
        pos = lambda state: state.id not in state_ids \
            and 100 or state_ids.index(state.id) + 1

        states.sort(key=pos)
        return states

    def get_hidden_roles(self):
        return []

    def _translate(self, *args, **kwargs):
        kwargs.update({'context': self.workflow.REQUEST})
        return translate(*args, **kwargs)
