# -*- coding: utf-8 -*-


from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zopyx.typesense import _
from zopyx.typesense.interfaces import ITypesenseSettings

import json


class TypesenseSettingsEditForm(controlpanel.RegistryEditForm):

    schema = ITypesenseSettings
    label = _(u"Typesense settings")
    description = _(u"")

    def updateFields(self):
        super(TypesenseSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(TypesenseSettingsEditForm, self).updateWidgets()


class TypesenseSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = TypesenseSettingsEditForm

    @property
    def settings(self):
        """Returns setting as dict"""
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITypesenseSettings)
        result = dict()
        for name in settings.__schema__:
            result[name] = getattr(settings, name)
        return result

    def settings_json(self):
        """Returns setting as JSON"""
        return json.dumps(self.settings)
