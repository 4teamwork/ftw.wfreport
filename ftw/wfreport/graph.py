from Products.DCWorkflow.interfaces import IDCWorkflowDefinition
from ftw.wfreport.dict_object import DictObject
from ftw.wfreport.interfaces import IGraphCreator
from ftw.wfreport.interfaces import IWorkflowDataProvider
from pygraphviz import AGraph
from zope.component import adapts
from zope.component import getAdapter
from zope.interface import implements
import os


class WorkflowCreator(object):
    implements(IGraphCreator)
    adapts(IDCWorkflowDefinition)

    def __init__(self, workflow):
        self.workflow = workflow

    def __call__(self, directory, basename):
        data = getAdapter(self.workflow, IWorkflowDataProvider)
        self._footnotes = []

        graph = self._create_graph()
        self._create_nodes(graph, data)
        self._create_edges(graph, data)
        self._create_files(graph, directory, basename)

        return self._footnotes

    def _create_graph(self):
        graph = AGraph(
            directed=True,
            strict=False,
            concentrate=False,
            nodesep='0.5',
            layout='dot',
            rankdir="TB",
            size='7.75,10.25')

        graph.node_attr.update(fontsize=18)

        return graph

    def _create_nodes(self, graph, data):
        for state in data.get_states():
            graph.add_node(state.id, label=state.title)

    def _create_edges(self, graph, data):
        for edge in self._get_ordered_edge_data(data):
            graph.add_edge(*edge.args, **edge.kwargs)

    def _get_edge_data(self, data):
        edges = {}

        states = data.get_states()

        for i, state in enumerate(states):
            for transition in state.transitions:
                key = (state.id, transition.destination.id)

                if key in edges:
                    edges[key].title.append(transition.title)
                    edges[key].roles.extend(
                        data.get_allowed_roles(transition, state))

                else:
                    edges[key] = DictObject({
                            'args': key,
                            'title': [transition.title],
                            'roles': data.get_allowed_roles(transition, state),
                            'kwargs': {}})

        for edge in edges.values():
            label = '\\n'.join(edge.title)

            if edge.roles:
                num = self._add_footnote(', '.join(
                        [role.title for role in edge.roles]))
                label = '%s (%s)' % (label, num)

            edge.kwargs['label'] = label

        return edges

    def _get_ordered_edge_data(self, data):
        edges = self._get_edge_data(data)

        # The order is very important for influencing the layout of the graph.
        states = data.get_states()

        # - start yielding the direct edges in node order (as states are sorted)
        for i, state in enumerate(states):
            next_state_id = i < len(states) - 1 and states[i + 1].id or None

            key = (state.id, next_state_id)
            if key in edges:
                # Add additional weight so that the nodes are layouted in a row
                edges[key].kwargs['weight'] = 10

                yield edges[key]
                del edges[key]

        # - then yield all other transitions in state order
        for state in states:
            for key, value in edges.items():
                if key[0] == state.id:
                    yield value
                    del edges[key]

        assert len(edges) == 0

    def _add_footnote(self, text):
        if text in self._footnotes:
            return self._footnotes.index(text) + 1
        else:
            self._footnotes.append(text)
            return len(self._footnotes)

    def _create_files(self, graph, directory, basename):
        if not os.path.isdir(directory):
            raise OSError('Not a directory: "%s"' % directory)

        basepath = os.path.join(directory, basename)
        graph.write('%s.dot' % basepath)
        graph.layout()
        graph.draw('%s.pdf' % basepath, prog='dot', format='pdf')
