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
# Mon 21 Oct 14:25:18 CEST 2019

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language
from gerenuk_dashboard.content.alerts import tables as alerts_tables
from gerenuk_dashboard.content.alerts import tables as alerts_en_tables
from gerenuk_dashboard.content.alerts import tables as user_tables
from gerenuk_dashboard.content.alerts import tables as user_en_tables
from openstack_auth import utils as user_acces
from horizon.tables import MultiTableView
from collections import namedtuple
import gerenuk
import gerenuk.api


# TODO: To move to local_settings.py
ROLE = 'project_manager'


#def verify(self,name):
#    """
#    TODO
#    """
#    roles = user_acces.get_user(self.request).roles
#    for r in roles:
#        if r['name'] == name :
#            return True
#    return False


#def ret(request):
#    """
#    TODO
#    """
#    return request


class AlertsTables(MultiTableView):
    """
    """
    table_classes = (
        alerts_tables.AlertsTable,
        alerts_en_tables.AlertsEnTable,
        user_tables.UserTable,
        user_en_tables.UserEnTable
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
        TODO
        """
        context = super(AlertsTables, self).get_context_data(**kwargs)
        context['lang'] = get_language()
        return context


    def get_alerts_data(self):
        """
        TODO
        """
        config = gerenuk.Config()
        # TODO: use const defined in local_settings.py
        config.load('/etc/gerenuk/gerenuk.conf')

        api = gerenuk.api.AlertsAPI(config)
        project = user_acces.get_user(self.request).project_id
        unread_alerts = api.get_unread_alerts(project)

        #print ("this is the PM alerts")
        #print user_acces.get_client_ip(self.request)

        my_alerts = []
        #if self.verify(ROLE):
        for l in range(0, len(unread_alerts)):
            if not(unread_alerts[l]["uuid"]):
                un_alerts = []
                un_alerts.append(unread_alerts[l])
                for alert in un_alerts:
                    alert_named = [namedtuple("Alert", alert.keys())(*alert.values())]
                    for a in alert_named:
                        my_alerts.append(a)
        return my_alerts
     
        
    def get_user_data(self):
        """
        TODO
        """
        config = gerenuk.Config()
        # TODO: use const defined in local_settings.py
        config.load('/etc/gerenuk/gerenuk.conf')

        api = gerenuk.api.AlertsAPI(config)
        project = user_acces.get_user(self.request).project_id
        unread_alerts = api.get_unread_alerts(project)

        user_alerts = []

        for l in range(0,len(unread_alerts)):
            if (unread_alerts[l]["uuid"] == user_acces.get_user(self.request).id) and not(self.verify(ROLE)):
                un_alerts = []
                un_alerts.append(unread_alerts[l])
                for alert in un_alerts:
                    alert_named = [namedtuple("Alert", alert.keys())(*alert.values())]
                    for a in alert_named:
                        user_alerts.append(a)
            elif (self.verify(ROLE)) and (unread_alerts[l]["uuid"]) :
                un_alerts = []
                un_alerts.append(unread_alerts[l])
                for alert in un_alerts:
                    alert_named = [namedtuple("Alert", alert.keys())(*alert.values())]
                    for a in alert_named:
                        user_alerts.append(a)
            else :
                continue
        return user_alerts


    def get_alerts_en_data(self):
        """
        TODO
        """
        return self.get_alerts_data()


    def get_user_en_data(self):
        """
        TODO
        """
        return self.get_user_data()
