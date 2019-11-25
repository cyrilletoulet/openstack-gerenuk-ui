# -*- coding: utf-8 -*-
# This file is part of Gerenuk.
#
# Gerenuk is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# Gerenuk is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Gerenuk. If not, see <https://www.gnu.org/licenses/>.
#
# Cyrille TOULET <cyrille.toulet@univ-lille.fr>
# Iheb ELADIB <iheb.eladib@univ-lille.fr>
#
# Mon 25 Nov 09:22:28 CET 2019

import gerenuk
import gerenuk.api

from openstack_auth import utils as os_auth

from django.conf import settings
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables


# Constants
SEVERITY = {
    0: "INFO", 
    1: "ALERT", 
    2: "WARNING",
    3: "CRITICAL",
}

SEVERITY_CHOICES = (
    ("INFO", "Info"),
    ("ALERT", "Alert"),
    ("WARNING", "Warning"),
    ("CRITICAL", "Critical"),
)


# Functions
def get_severity(alert_named):
    """
    Get the severity of an alert.
    :param alert_named: (namedtuple) The alert named tuple
    :return: (str) The severity string
    """
    return SEVERITY.get(getattr(alert_named, "severity", 0), "")


# Classes
class MarkUserAlertsAsRead(tables.DeleteAction):
    """
    The horizon table used to delete user alerts.
    """
    name = "read" 
    help_text = _("Don't forget to solve the problem before marking an alert as read.")
    default_message_level = "info"


    @staticmethod
    def action_present(count):
        """
        Define action labels shown on page.
        """
        return ungettext_lazy(u"Mark alert as read", u"Mark them as read", count)


    @staticmethod
    def action_past(count):
        """
        Define message shown after action validation.
        """
        return ungettext_lazy(u"Scheduled deletion of alert", u"Scheduled deletion of alerts", count)


    def get_object_id(self, datum):
        """
        Get alert id.
        """
        return datum.id
    
        
    def delete(self, request, obj_id):
        """
        Action called to define if the current user is allowed to mark alerts as read.
        """
        gerenuk_config = gerenuk.Config()
        gerenuk_config.load(settings.GERENUK_CONF)
        gerenuk_api = gerenuk.api.AlertsAPI(gerenuk_config)

        project = os_auth.get_user(request).project_id
        unread_alerts = gerenuk_api.get_unread_alerts(project)
        read_ids = list()

        for i in range(0, min(1, len(unread_alerts))):
            read_ids.append(unread_alerts[i]["id"])

        gerenuk_api.tag_alerts_as_read([int(obj_id)])



class UserAlertsTable(tables.DataTable):
    """
    The horizon table used to display user alerts.
    """
    name = tables.Column("username", verbose_name=_("Username"))

    if get_language() == "fr":
        message = tables.Column("message_fr", verbose_name=_("Message"))
    else:
        message = tables.Column("message_en", verbose_name=_("Message"))
    id = tables.Column("id", verbose_name=_("Id "))
    severity = tables.Column(get_severity, verbose_name=_("Severity"), sortable= True, display_choices=SEVERITY_CHOICES)
    created = tables.Column("timestamp" , verbose_name=_("Updated"))


    def get_object_id(self, datum):
        """
        Get alert id.
        """
        return datum.id

    def get_object_display(self, datum):
        """
        Display id to be deleted
        """
        return datum.id


    class Meta(object):
        """
        Define metadata.
        """
        name = "user_alerts"
        verbose_name = _("User alerts")
        status_columns = ["severity",]
        table_actions = (MarkUserAlertsAsRead,)
        row_actions = (MarkUserAlertsAsRead,)

        

class MarkProjectAlertsAsRead(tables.DeleteAction):
    """
    The horizon table used to mark project alerts as read.
    """
    name = "read" 
    help_text = _("Don't forget to solve the problem before marking an alert as read.")
    default_message_level = "info"

    
    @staticmethod
    def action_present(count):
        """
        Define action labels shown on page.
        """
        return ungettext_lazy(u"Mark alert as read", u"Mark them as read", count)


    @staticmethod
    def action_past(count):
        """
        Define message shown after action validation.
        """
        return ungettext_lazy(u"Scheduled deletion of alert", u"Scheduled deletion of alerts", count)


    def get_object_id(self, datum):
        """
        Get alert id.
        """
        return datum.id
    
        
    def allowed(self, request, user_alerts=None):
        """
        Define if the current user is allowed to mark alerts as read.
        """
        roles = os_auth.get_user(request).roles
        
        for r in roles :
            if r["name"] == settings.PROJECT_MANAGER_ROLE:
                return True

        return False


    def delete(self, request, obj_id):
        """
        Action called to mark an alert as read.
        """
        gerenuk_config = gerenuk.Config()
        gerenuk_config.load(settings.GERENUK_CONF)
        gerenuk_api = gerenuk.api.AlertsAPI(gerenuk_config)

        project = os_auth.get_user(request).project_id
        unread_alerts = gerenuk_api.get_unread_alerts(project)
        read_ids = list()
        
        for i in range(0, min(1, len(unread_alerts))):
            read_ids.append(unread_alerts[i]["id"])

        gerenuk_api.tag_alerts_as_read([int(obj_id)])


        
class ProjectAlertsTable(tables.DataTable):
    """
    The horizon table used to display project alerts.
    """
    project = tables.Column("project", verbose_name=_("Project"))
    if get_language() == "fr":
        message = tables.Column("message_fr", verbose_name=_("Message"))
    else:
        message = tables.Column("message_en", verbose_name=_("Message"))
    id = tables.Column("id", verbose_name=_("Id "))
    severity = tables.Column(get_severity, verbose_name=_("Severity"), sortable= True, display_choices=SEVERITY_CHOICES)
    created = tables.Column("timestamp" , verbose_name=_("Updated"))

    
    def get_object_id(self, datum):
        """
        Get alert id.
        """
        return datum.id
       

    class Meta(object):
        """
        Define metadata.
        """
        name = "project_alerts"
        verbose_name = _("Project alerts")
        status_columns = ["severity",]
        table_actions = (MarkProjectAlertsAsRead,)
        row_actions = (MarkProjectAlertsAsRead,)


        
class ReadAlertsTable(tables.DataTable):
    """
    The horizon table used to display read alerts.
    """
    project = tables.Column("project", verbose_name=_("Project"))
    if get_language() == "fr":
        message = tables.Column("message_fr", verbose_name=_("Message"))
    else:
        message = tables.Column("message_en", verbose_name=_("Message"))
    id = tables.Column("id", verbose_name=_("Id"))
    severity = tables.Column(get_severity, verbose_name=_("Severity"), sortable= True, display_choices=SEVERITY_CHOICES)
    created = tables.Column("timestamp" , verbose_name=_("Updated"))


    def get_object_id(self, datum):
        """
        Get alert id.
        """
        return datum.id


    def get_object_display(self, datum):
        """
        Display id to be deleted
        """
        return datum.id


    class Meta(object):
        """
        Define metadata.
        """
        name = "read_alerts"
        verbose_name = _("Read alerts")
        status_columns = ["severity",]
