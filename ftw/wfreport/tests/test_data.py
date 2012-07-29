from Products.CMFCore.utils import getToolByName
from ftw.wfreport.data import map_by_key
from ftw.wfreport.interfaces import IWorkflowDataProvider
from ftw.wfreport.testing import FTW_WFREPORT_INTEGRATION_TESTING
from unittest2 import TestCase
from zope.component import getAdapter


class TestMapByKey(TestCase):

    def test(self):
        input = [{'id': 'foo', 'title': 'FOO'},
                 {'id': 'bar', 'title': 'BAR'}]

        output = {'foo': {'id': 'foo', 'title': 'FOO'},
                  'bar': {'id': 'bar', 'title': 'BAR'}}

        self.assertEqual(map_by_key(input), output)


class TestWorkflowDataProvider(TestCase):

    layer = FTW_WFREPORT_INTEGRATION_TESTING

    def setUp(self):
        super(TestWorkflowDataProvider, self).setUp()

        portal = self.layer['portal']
        wftool = getToolByName(portal, 'portal_workflow')

        wf = wftool.get('simple_publication_workflow')
        self.data = getAdapter(wf, IWorkflowDataProvider)

    def test_get_states(self):
        states = self.data.get_states()
        self.assertEquals(len(states), 3)
        self.assertEquals(set(states[0].keys()),
                          set(['id', 'title', 'transitions', 'permission_mapping',
                               'initial']))

        mapped_states = map_by_key(states)
        self.assertIn('private', mapped_states)
        self.assertIn('pending', mapped_states)
        self.assertIn('published', mapped_states)

    def test_state_metadata(self):
        pending = self.data.get_state_by_id('pending')
        self.assertEqual(pending.id, 'pending')
        self.assertEqual(pending.title, 'pending')
        self.assertEqual(pending.initial, False)

        private = self.data.get_state_by_id('private')
        self.assertEqual(private.initial, True)

    def test_state_transitions(self):
        pending = self.data.get_state_by_id('pending')
        transitions = map_by_key(pending.transitions)
        self.assertIn('publish', transitions)
        self.assertIn('reject', transitions)
        self.assertIn('retract', transitions)

    def test_state_permission_mapping(self):
        pending = self.data.get_state_by_id('pending')
        permissions = map_by_key(pending.permission_mapping)

        self.assertIn('View', permissions)
        self.assertEqual(permissions.View.id, 'View')
        self.assertEqual(permissions.View.title, 'View')

        self.assertEqual(set(map_by_key(permissions.View.roles).keys()),
                         set(['Contributor',
                              'Editor',
                              'Manager',
                              'Owner',
                              'Reader',
                              'Reviewer',
                              'Site Administrator']))

        self.assertEqual(map_by_key(permissions.View.roles).Owner,
                         self.data.get_role_by_id('Owner'))

    def test_nested_dicts(self):
        states = map_by_key(self.data.get_states())

        self.assertEqual(
            map_by_key(states.pending.transitions).reject.destination,
            states.private)
