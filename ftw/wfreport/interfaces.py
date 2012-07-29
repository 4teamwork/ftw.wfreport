from ftw.table.interfaces import ITableSourceConfig
from zope.interface import Interface


class IWorkflowsTableSourceConfig(ITableSourceConfig):
    """Table source config interface for workflows.
    """
class IWorkflowDataProvider(Interface):
    """Provides workflow data.
    The data is generally provided as dicts which are also accesible in
    an attribute like manner.
    """

    def __init__(workflow):
        """Adapts the DC workflow definition.
        """

    def get_states():
        """Returns a list of states, each represented as a dict
        of form::

        >>> {'id': 'state id',
        ...  'title': 'translated state title',
        ...  'transitions': [<transition as dict, see get_transitions()>],
        ...  'permission_mapping': <result of .get_permission_mapping()>,
        ...  'initial': True}
        """

    def get_state_by_id(state_id):
        """Returns the state with the id ``state_id``, represented as dict.
        See get_states().
        """

    def get_roles():
        """Returns a list of roles, each represented as a dict
        of form::

        >>> {'id': 'role id',
        ...  'title': 'translated role title'}
        """

    def get_role_by_id(role_id):
        """Returns the role with the id ``role_id``, represented as dict.
        See get_roles().
        """

    def get_permission_mapping(state_id):
        """Returns a permission mapping for the state ``state_id``. The mapping
        is a list of permissions and the mapped roles in the form::

        >>> {'id': 'full permission name',
        ...  'title': 'translated permission title, if available',
        ...  'roles': <mapped roles list as in get_roles()>}
        """

    def get_transitions():
        """Returns a list of transitions, each represented as a dict
        of form::

        >>> {'id': 'transition id',
        ...  'title': 'translated transition title',
        ...  'destination': <state as in get_states>}
        """

    def get_transition_by_id(transition_id):
        """Returns the transition with the id ``transition_id``,
        represented as dict.
        See get_transitions().
        """
