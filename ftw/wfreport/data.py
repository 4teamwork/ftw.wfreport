from Products.DCWorkflow.interfaces import IDCWorkflowDefinition
from ftw.wfreport.dict_object import DictObject
from ftw.wfreport.interfaces import IWorkflowDataProvider
from plone.app.workflow.interfaces import ISharingPageRole
from zope.component import adapts
from zope.component import queryUtility
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import implements


def map_by_key(items, key='id'):
    """Creates a dict from a list of dicts.
    """
    return DictObject(map(lambda item: (item.get(key), item), items))


class WorkflowDataProvider(object):
    implements(IWorkflowDataProvider)
    adapts(IDCWorkflowDefinition)

    def __init__(self, workflow):
        self.workflow = workflow
        self._parsed = False
        self._states = None
        self._roles = None
        self._transitions = None

    def get_states(self):
        self._parse()
        return self._states

    def get_state_by_id(self, state_id):
        self._parse()
        return map_by_key(self._states).get(state_id)

    def get_roles(self):
        self._parse()
        return self._roles

    def get_role_by_id(self, role_id):
        self._parse()
        return map_by_key(self._roles).get(role_id)

    def get_permission_mapping(self, state_id):
        return self._states.get(state_id)

    def get_transitions(self):
        return self._transitions

    def get_transition_by_id(self, transition_id):
        self._parse()
        return map_by_key(self._transitions).get(transition_id)

    def _parse(self, reparse=False):
        """Parses the workflow definition if necessary.
        """

        if self._parsed and not reparse:
            return
        self._parsed = True

        self._parse_roles()
        self._parse_states()
        self._parse_transitions()
        self._add_transitions_to_states()

    def _parse_states(self):
        self._states = []
        for state in self.workflow.states.values():
            self._states.append(DictObject({
                        'id': state.id,
                        'title': self._translate(state.id),
                        'transitions': -1,  # not yet loaded
                        'permission_mapping': self._parse_permission_roles_for_state(
                            state),
                        'initial': state.id == self.workflow.initial_state,
                        }))

    def _parse_permission_roles_for_state(self, state):
        result = []
        for permission, roles in state.permission_roles.items():
            result.append(DictObject({
                        'id': permission,
                        'title': self._translate(permission, domain='ftw.wfreport'),
                        'roles': [self.get_role_by_id(role)
                                  for role in roles]}))

        return result

    def _parse_roles(self):
        self._roles = []
        for role_id in self.workflow.getAvailableRoles():
            role_title = role_id

            role_utility = queryUtility(ISharingPageRole, name='Administrator')
            if role_utility:
                role_title = self._translate(role_utility.title)

            self._roles.append(DictObject({
                        'id': role_id,
                        'title': role_title}))

    def _parse_transitions(self):
        self._transitions = []
        for obj in self.workflow.transitions.values():
            self._transitions.append(DictObject({
                        'id': obj.id,
                        'title': self._translate(obj.title),
                        'destination': self.get_state_by_id(obj.new_state_id)}))

    def _add_transitions_to_states(self):
        for state in self.get_states():
            state_obj = self.workflow.states.get(state.id)
            state['transitions'] = []

            for transition_id in state_obj.transitions:
                if self.get_transition_by_id(transition_id) is None:
                    continue

                state['transitions'].append(
                    self.get_transition_by_id(transition_id))

    def _translate(self, text, domain='plone'):
        return translate(MessageFactory(domain)(text),
                         context=self.workflow.REQUEST)
