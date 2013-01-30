from Products.DCWorkflow.interfaces import IDCWorkflowDefinition
from ftw.wfreport.dict_object import DictObject
from ftw.wfreport.interfaces import IWorkflowDataProvider
from ftw.wfreport.interfaces import IWorkflowReportConfig
from plone.app.workflow.interfaces import ISharingPageRole
from zope.component import adapts
from zope.component import getAdapter
from zope.component import queryAdapter
from zope.component import queryUtility
from zope.i18n import translate
from zope.i18nmessageid import Message
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
        self._config = None
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

    def get_role_by_id(self, role_id, default=None):
        self._parse()
        return map_by_key(self._roles).get(role_id, default)

    def get_permission_mapping(self, state_id):
        return self._states.get(state_id)

    def get_transitions(self):
        return self._transitions

    def get_transition_by_id(self, transition_id):
        self._parse()
        return map_by_key(self._transitions).get(transition_id)

    def get_allowed_roles(self, transition, state):
        wfstate = self.workflow.states.get(state.id)
        roles = set([])

        for role_id in transition.role_guard:
            role = self.get_role_by_id(role_id)
            if role:
                roles.add(role)

        for permission in transition.permission_guard:
            if not wfstate.permission_roles:
                continue

            perm = wfstate.permission_roles.get(permission)
            if not perm:
                continue

            for role_id in perm:
                role = self.get_role_by_id(role_id)
                if role:
                    roles.add(role)

        return roles

    def _parse(self, reparse=False):
        """Parses the workflow definition if necessary.
        """

        if self._parsed and not reparse:
            return
        self._parsed = True
        self._load_config()

        self._parse_roles()
        self._parse_states()
        self._parse_transitions()
        self._add_transitions_to_states()

    def _load_config(self):
        self._config = queryAdapter(self.workflow, IWorkflowReportConfig,
                                    name=self.workflow.id)
        if not self._config:
            self._config = getAdapter(self.workflow, IWorkflowReportConfig)

    def _parse_states(self):
        states = []
        for state in self.workflow.states.values():
            states.append(DictObject({
                        'id': state.id,
                        'title': self._translate(state.id),
                        'transitions': -1,  # not yet loaded
                        'permission_mapping': self._parse_permission_roles_for_state(
                            state),
                        'initial': state.id == self.workflow.initial_state,
                        }))

        self._states = self._config.order_states(states)

    def _parse_permission_roles_for_state(self, state):
        result = []

        hidden = self._config.get_hidden_permissions()
        merged = self._config.get_merged_permissions_mapped_by_permission()
        merged_inserted = {}

        if not state.permission_roles:
            return []

        for permission, roles in state.permission_roles.items():
            if permission in hidden:
                continue

            if permission in merged and \
                    merged[permission]['title'] not in merged_inserted:
                merge = merged[permission]
                data = DictObject({
                        'id': merge['title'],
                        'title': merge['title'],
                        'roles': [self.get_role_by_id(role)
                                  for role in roles if self.get_role_by_id(role)],
                        'merged': [self._translate(perm) for perm
                                   in merge['permissions']
                                   if perm in state.permission_roles.keys()]})

                result.append(data)
                merged_inserted[merge['title']] = data

            elif permission in merged:
                merge = merged[permission]
                data = merged_inserted[merge['title']]
                roles = set(data.roles)
                roles.update([self.get_role_by_id(role) for role in roles
                              if self.get_role_by_id(role)])
                data.roles = list(roles)

            else:
                result.append(DictObject({
                            'id': permission,
                            'title': self._translate(permission,
                                                     domain='ftw.wfreport'),
                            'roles': [self.get_role_by_id(role)
                                      for role in roles
                                      if self.get_role_by_id(role)]}))

        result.sort(key=lambda permission: permission.title)
        return result

    def _parse_roles(self):
        self._roles = []
        hidden = self._config.get_hidden_roles()

        for role_id in self.workflow.getAvailableRoles():
            if role_id in hidden:
                continue

            role_title = self._translate(role_id, domain='ftw.wfreport')
            role_utility = queryUtility(ISharingPageRole, name=role_id)
            if role_utility:
                role_title = self._translate(role_utility.title)

            self._roles.append(DictObject({
                        'id': role_id,
                        'title': role_title}))

    def _parse_transitions(self):
        self._transitions = []
        for obj in self.workflow.transitions.values():
            role_guard_text = obj.getGuard().getRolesText().strip()
            if role_guard_text:
                role_guard = [role.strip() for role
                              in role_guard_text.split(';')]
            else:
                role_guard = []

            permission_guard_text = obj.getGuard().getPermissionsText().strip()
            if permission_guard_text:
                permission_guard = [permission.strip() for permission
                                    in permission_guard_text.split(';')]
            else:
                permission_guard = []

            self._transitions.append(DictObject({
                        'id': obj.id,
                        'title': self._translate(obj.title),
                        'destination': self.get_state_by_id(obj.new_state_id),
                        'role_guard': role_guard,
                        'permission_guard': permission_guard}))

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
        if not isinstance(text, Message):
            text = MessageFactory(domain)(text)

        return translate(text, context=self.workflow.REQUEST)
