from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig


class FtwWfreportLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ftw.wfreport
        xmlconfig.file('configure.zcml', ftw.wfreport,
                       context=configurationContext)


FTW_WFREPORT_FIXTURE = FtwWfreportLayer()
FTW_WFREPORT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_WFREPORT_FIXTURE,), name="FtwWfreport:Integration")
