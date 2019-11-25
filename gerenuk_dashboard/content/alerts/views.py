# coding: utf8
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
# Mon 25 Nov 09:25:47 CET 2019

import gerenuk
import gerenuk.api

from collections import namedtuple

from openstack_auth import utils as os_auth
from openstack_dashboard import api

from django.urls import reverse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from horizon.tables import MultiTableView, DataTableView
from gerenuk_dashboard.content.alerts import tables
from gerenuk_dashboard.content import helpers


class AlertsTables(MultiTableView):
    """
    The alerts view.
    """
    table_classes = (
        tables.ProjectAlertsTable,
        tables.UserAlertsTable,
    )
    template_name = "project/alerts/index.html"
    page_title = _("Alerts")


    def get_context_data(self, **kwargs):
        """
        Define the view context
        """
        context = super(AlertsTables, self).get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["archives_url"] = reverse("horizon:project:alerts:archives")
        context["is_project_manager"] = helpers.has_role(self.request ,settings.PROJECT_MANAGER_ROLE)
        
        return context

        
    def get_project_alerts_data(self):
        """
        Getter used by ProjectAlertsTable model.
        """
        gerenuk_config = gerenuk.Config()
        gerenuk_config.load(settings.GERENUK_CONF)
        gerenuk_api = gerenuk.api.AlertsAPI(gerenuk_config)

        project = os_auth.get_user(self.request).project_id
        unread_alerts = gerenuk_api.get_unread_alerts(project)

        project_alerts = []

        for l in range(0, len(unread_alerts)):
            if not(unread_alerts[l]["uuid"]):
                un_alerts = []
                un_alerts.append(unread_alerts[l])

                for alert in un_alerts:
                    alert_named = [namedtuple("Alert", alert.keys())(*alert.values())]

                    for a in alert_named:
                        project_alerts.append(a)

        return project_alerts
     
        
    def get_user_alerts_data(self):
        """
        Getter used by UserAlertsTable model.
        """
        gerenuk_config = gerenuk.Config()
        gerenuk_config.load(settings.GERENUK_CONF)
        gerenuk_api = gerenuk.api.AlertsAPI(gerenuk_config)

        project = os_auth.get_user(self.request).project_id
        username = os_auth.get_user(self.request).username
        unread_alerts = gerenuk_api.get_unread_alerts(project)
        user_alerts = []
        users_cache = dict()


        for l in range(0, len(unread_alerts)):
              if (helpers.has_role(self.request, settings.PROJECT_MANAGER_ROLE)) and (unread_alerts[l]["uuid"]) :

                un_alerts = []
                user_id = str(unread_alerts[l]["uuid"])
                if not user_id in users_cache:
                    user = api.keystone.user_get(self.request, user_id, admin=False)
                    users_cache[user_id] = user.name
                    if user.description:
                       users_cache[user_id] += " (" + user.description + ")"

                unread_alerts[l].update({'username': users_cache[user_id]})
                un_alerts.append(unread_alerts[l])

                for alert in un_alerts:
                    alert_named = [namedtuple("Alert", alert.keys())(*alert.values())]

                    for a in alert_named:
                        user_alerts.append(a)

              elif (unread_alerts[l]["uuid"] == os_auth.get_user(self.request).id):

                un_alerts = []
                username = os_auth.get_user(self.request).username
                unread_alerts[l].update({'username': username})
                un_alerts.append(unread_alerts[l])
                
                for alert in un_alerts:
                    alert_named = [namedtuple("Alert", alert.keys())(*alert.values())]
                    
                    for a in alert_named:
                        user_alerts.append(a)

        return user_alerts


    
class ReadAlerts(DataTableView):
    """
    The read alerts view.
    """
    table_class = tables.ReadAlertsTable
    template_name = 'project/alerts/read.html'
    page_title = _("Archives")


    def get_context_data(self, **kwargs):
        """
        Define the view context
        """
        context = super(ReadAlerts, self).get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["back_to_alerts_url"] = reverse("horizon:project:alerts:index")
        context["is_project_manager"] = helpers.has_role(self.request ,settings.PROJECT_MANAGER_ROLE)
        
        return context


    def get_data(self):
        """
        Getter used by ReadedAlertsTable model.
        """
        gerenuk_config = gerenuk.Config()
        gerenuk_config.load(settings.GERENUK_CONF)
        gerenuk_api = gerenuk.api.AlertsAPI(gerenuk_config)

        project = os_auth.get_user(self.request).project_id
        read_alerts = gerenuk_api.get_read_alerts(project)

        tagged_alerts = []

        for l in range(0, len(read_alerts)):
            if (read_alerts[l]["uuid"]) and (helpers.has_role(self.request, settings.PROJECT_MANAGER_ROLE)):
                re_alerts = []
                re_alerts.append(read_alerts[l])

                for alert in re_alerts:
                    alert_named = [namedtuple("Alert", alert.keys())(*alert.values())]

                    for a in alert_named:
                        tagged_alerts.append(a)
            else :
                tagged_alerts = []
        return tagged_alerts
