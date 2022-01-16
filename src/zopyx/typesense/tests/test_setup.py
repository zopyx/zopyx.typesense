# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from zopyx.typesense.testing import (
    ZOPYX_TYPESENSE_INTEGRATION_TESTING,
)  # noqa: E501

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that zopyx.typesense is properly installed."""

    layer = ZOPYX_TYPESENSE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if zopyx.typesense is installed."""
        self.assertTrue(self.installer.isProductInstalled("zopyx.typesense"))

    def test_browserlayer(self):
        """Test that IZopyxTypesenseLayer is registered."""
        from zopyx.typesense.interfaces import IZopyxTypesenseLayer
        from plone.browserlayer import utils

        self.assertIn(IZopyxTypesenseLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = ZOPYX_TYPESENSE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstallProducts(["zopyx.typesense"])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if zopyx.typesense is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled("zopyx.typesense"))

    def test_browserlayer_removed(self):
        """Test that IZopyxTypesenseLayer is removed."""
        from zopyx.typesense.interfaces import IZopyxTypesenseLayer
        from plone.browserlayer import utils

        self.assertNotIn(IZopyxTypesenseLayer, utils.registered_layers())
