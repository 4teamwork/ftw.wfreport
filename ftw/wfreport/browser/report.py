from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.interfaces import IDCWorkflowDefinition
from ftw.pdfgenerator.browser.standalone import BaseStandalonePDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.layout.makolayout import MakoLayoutBase
from ftw.pdfgenerator.view import MakoLaTeXView
from ftw.wfreport.interfaces import IGraphCreator
from ftw.wfreport.interfaces import IWorkflowDataProvider
from ftw.wfreport.interfaces import IWorkflowReportConfig
from ftw.wfreport.interfaces import IWorkflowsReportLayout
from zope.component import adapts
from zope.component import getAdapter
from zope.component import queryAdapter
from zope.i18n import translate
from zope.interface import Interface
from zope.interface import implements


class WorkflowsReport(BaseStandalonePDFView):
    implements(IWorkflowsReportLayout)

    template_directories = ['latex']
    template_name = 'report.tex'

    def get_views_for(self, obj):
        if obj is self.context:
            # This is the main view.
            return [self]

        else:
            # We are rendering workflows, so we delegate.
            return MakoLayoutBase.get_views_for(self, obj)

    def render(self):
        # Render the view means rendering all selected workflows.
        wftool = getToolByName(self.context, 'portal_workflow')

        latex = []

        for wfid in self.request.get('paths'):
            workflow = wftool.get(wfid)
            latex.append(self.render_latex_for(workflow))

        return '\n'.join(latex)

    def before_render_hook(self):
        self.use_babel()
        self.use_package('inputenc', options='utf8', append_options=False)
        self.use_package('fontenc', options='T1', append_options=False)
        self.use_package('ae,aecompl')
        self.use_package(
            'geometry', options='left=1cm,right=1cm,top=1cm,bottom=2cm',
            append_options=False)

        self.use_package('helvet')
        self.use_package('longtable')
        self.use_package('rotating')


class WorkflowLaTeXView(MakoLaTeXView):
    implements(ILaTeXLayout)
    adapts(IDCWorkflowDefinition, Interface, IWorkflowsReportLayout)

    template_directories = ['latex']
    template_name = 'workflow.tex'

    def get_render_arguments(self):
        args = super(WorkflowLaTeXView, self).get_render_arguments()
        data = getAdapter(self.context, IWorkflowDataProvider)

        footnotes = self.create_graph()

        args.update({
                'title': self.context.title,
                'data': data,
                '_': lambda text: translate(
                    text, domain='ftw.wfreport', context=self.request),
                'convert': self.convert,
                'translate_permissions': self.translate_permissions,
                'graph': '%s.pdf' % self.context.id,
                'footnotes': footnotes})
        return args

    def translate_permissions(self, permissions):
        translated = []
        hidden_permissions = self._get_config().get_hidden_permissions()

        for permission in permissions:
            if permission in hidden_permissions:
                continue

            translated.append(
                translate(permission, domain='ftw.wfreport', context=self.request))

        return self.convert(', '.join(translated))

    def _get_config(self):
        config = queryAdapter(self.context, IWorkflowReportConfig,
                                    name=self.context.id)
        if not config:
            config = getAdapter(self.context, IWorkflowReportConfig)

        return config

    def create_graph(self):
        creator = getAdapter(self.context, IGraphCreator)
        return creator(self.layout.get_builder().build_directory, self.context.id)
