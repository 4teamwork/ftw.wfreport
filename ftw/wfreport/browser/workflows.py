from Products.CMFCore.utils import getToolByName
from ftw.tabbedview.browser.listing import ListingView
from ftw.tabbedview.browser.tabbed import TabbedView
from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSource
from ftw.wfreport import _
from ftw.wfreport.interfaces import IWorkflowsTableSourceConfig
from zope.app.component.hooks import getSite
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements


def workflow_checkbox(item, value):
    return '<input type="checkbox" class="noborder selectable" ' + \
        'name="paths:list" id="%s" value="%s" />' % (item.id, item.id)


class WorkflowsView(TabbedView):
    """Tabbed workflows view"""

    def get_tabs(self):
        return [{'id':'workflows', 'class':''}]


class WorkflowsTab(ListingView):
    """Tab listing all workflows.
    """

    implements(IWorkflowsTableSourceConfig)

    show_menu = True
    batching_enabled = True

    columns = (
        ('', workflow_checkbox),
        {'column': 'id'},
        {'column': 'title'})

    def get_base_query(self):
        return {}

    def major_buttons(self):
        return [{'title': _(u'button_generate_report',
                            default=u'Generate report'),
                 'url': '@@generate-workflow-report:method'}]


class WorkflowsTableSource(BaseTableSource):
    """Table source adapter for the workflows tab.
    """

    implements(ITableSource)
    adapts(IWorkflowsTableSourceConfig, Interface)

    def validate_base_query(self, query):
        assert isinstance(query, dict)
        return query

    def extend_query_with_ordering(self, query):
        query['sort_on'] = self.config.sort_on
        query['sort_reverse'] = self.config.sort_reverse
        return query

    def extend_query_with_textfilter(self, query, text):
        query['searchterm'] = text
        return query

    def extend_query_with_batching(self, query):
        # No lazy batching - batching is done by plone batch.
        # We need to load all workflows anyway.
        return query

    def search_results(self, query):
        wftool = getToolByName(getSite(), 'portal_workflow')
        items = list(wftool.objectValues())
        items = self._sort_results(items, query)
        items = self._filter_results(items, query)
        return items

    def _sort_results(self, items, query):
        def _sorter(item):
            value = getattr(item, query.get('sort_on'), None)
            if callable(value):
                value = value()
            return value

        items.sort(key=_sorter, reverse=query.get('sort_reverse'))
        return items

    def _filter_results(self, items, query):
        if 'searchterm' not in query:
            return items

        new_items = []
        term = query['searchterm']

        for item in items:
            searchtext = ' '.join((item.id, item.title))
            if term in searchtext:
                new_items.append(item)

        return new_items
