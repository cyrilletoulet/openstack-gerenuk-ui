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
# Tue 22 Oct 15:52:30 CEST 2019

import gerenuk
import gerenuk.api
from collections import namedtuple

from openstack_auth import utils as user_acces

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from horizon.tables import MultiTableView
from gerenuk_dashboard.content.alerts import tables


class AlertsTables(MultiTableView):
    """
    The alerts view.
    """
    table_classes = (
        tables.ProjectAlertsTable,
        tables.UserAlertsTable,
    )
    template_name = 'project/alerts/index.html'
    page_title = _("Alerts")


    def verify(self, name):
        """
        TODO
        """
        req = self.request      
        roles = user_acces.get_user(self.request).roles

        for r in roles:
            if r['name'] == name :
                return True

        return False


    def get_context_data(self, **kwargs):
        """
        Get the view context.
        """
        context = super(AlertsTables, self).get_context_data(**kwargs)
        return context


    def get_project_alerts_data(self):
        """
        Getter used by UserAlertsTable model.
        """
        gerenuk_config = gerenuk.Config()
        gerenuk_config.load(settings.GERENUK_CONF)
        gerenuk_api = gerenuk.api.AlertsAPI(gerenuk_config)

        project = user_acces.get_user(self.request).project_id
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
        Getter used by ProjectAlertsTable model.
        """
        gerenuk_config = gerenuk.Config()
        gerenuk_config.load(settings.GERENUK_CONF)
        gerenuk_api = gerenuk.api.AlertsAPI(gerenuk_config)

        project = user_acces.get_user(self.request).project_id
        unread_alerts = gerenuk_api.get_unread_alerts(project)
        user_alerts = []

        for l in range(0, len(unread_alerts)):
            if (unread_alerts[l]["uuid"] == user_acces.get_user(self.request).id) and not(self.verify(settings.PROJECT_MANAGER_ROLE)):
                un_alerts = []
                un_alerts.append(unread_alerts[l])

                for alert in un_alerts:
                    alert_named = [namedtuple("Alert", alert.keys())(*alert.values())]

                    for a in alert_named:
                        user_alerts.append(a)

            elif (self.verify(settings.PROJECT_MANAGER_ROLE)) and (unread_alerts[l]["uuid"]) :
                un_alerts = []
                un_alerts.append(unread_alerts[l])
                
                for alert in un_alerts:
                    alert_named = [namedtuple("Alert", alert.keys())(*alert.values())]
                    
                    for a in alert_named:
                        user_alerts.append(a)

        return user_alerts
