# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PLONE_FIXTURE,
    PloneSandboxLayer,
)
from plone.testing import z2

import zopyx.typesense


class ZopyxTypesenseLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity

        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=zopyx.typesense)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "zopyx.typesense:default")


ZOPYX_TYPESENSE_FIXTURE = ZopyxTypesenseLayer()


ZOPYX_TYPESENSE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(ZOPYX_TYPESENSE_FIXTURE,),
    name="ZopyxTypesenseLayer:IntegrationTesting",
)


ZOPYX_TYPESENSE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(ZOPYX_TYPESENSE_FIXTURE,),
    name="ZopyxTypesenseLayer:FunctionalTesting",
)


ZOPYX_TYPESENSE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        ZOPYX_TYPESENSE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="ZopyxTypesenseLayer:AcceptanceTesting",
)
