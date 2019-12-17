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
# Tue 26 Nov 15:43:03 CET 2019

import gerenuk
import collections

from horizon.tables import DataTableView
from django.urls import reverse
from horizon import exceptions

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from django.views.generic import TemplateView

from openstack_dashboard import api
from openstack_auth import utils as os_auth
from gerenuk_dashboard.content.monitoring import tables
from gerenuk_dashboard.content.exceptions import PermissionsError
from gerenuk_dashboard.content import helpers

# Charts definition
ChartDefHour = collections.namedtuple(
    "ChartDefHour",
    ("quota_key", "label", "used_phrase", "filters")
)

CHART_DEFS_HOUR = [
    {
        "title": _("Monitoring Hourly"),
        "charts_hourly": [
            ChartDefHour("mem", _("Memory"), None, None),
            ChartDefHour("vcpu", _("vCPU"), None, None),
            ChartDefHour("cpu", _("CPU"), None, None),
        ]
    }
]

ChartDefWeek = collections.namedtuple(
    "ChartDefHour",
    ("quota_key", "label", "used_phrase", "filters")
)

CHART_DEFS_WEEK = [
    {
        "title": _("Monitoring Weekly"),
        "charts_weekly": [
            ChartDefHour("mem", _("Memory"), None, None),
            ChartDefHour("vcpu", _("vCPU"), None, None),
            ChartDefHour("cpu", _("CPU"), None, None),
        ]
    }
]

ChartDefDay = collections.namedtuple(
    "ChartDefDay",
    ("quota_key", "label", "used_phrase", "filters")
)

CHART_DEFS_DAY = [
    {
        "title": _("Monitoring Daily"),
        "charts_daily": [
            ChartDefDay("mem", _("Memory"), None, None),
            ChartDefDay("vcpu", _("vCPU"), None, None),
            ChartDefDay("cpu", _("CPU"), None, None),
        ]
    }
]



class IndexView(DataTableView):
    """
    The instances view  
    """
    table_class = tables.InstancesTable
    template_name = "project/monitoring/index.html"
    page_title = _("Monitoring")


    def get_context_data(self, **kwargs):
        """
        Define the view context
        """
        context = super(IndexView, self).get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["is_project_manager"] = helpers.has_role(self.request ,settings.PROJECT_MANAGER_ROLE)
        return context

    def get_statistics(self, instance_id, **kwargs):
        """
        Returns statistics from Gerenuk
        """
        gerenuk_config = gerenuk.Config()
        gerenuk_config.load(settings.GERENUK_CONF)
        gerenuk_api = gerenuk.api.InstancesMonitorAPI(gerenuk_config)

        uuid = list()
        uuid.append(str(instance_id))
        results = gerenuk_api.get_instances_monitoring(uuid)

        return results
   

 
    def get_data(self):
        """
        Getter used by the InstancesTable model
        """
        my_instances = []
        instances, self._more = api.nova.server_list(self.request)
        users_cache = dict()
        
        for instance in instances:
            if helpers.has_role(self.request, settings.PROJECT_MANAGER_ROLE):
                user_id = instance.user_id
                if not user_id in users_cache:
                    user = api.keystone.user_get(self.request, user_id, admin=False)
                    users_cache[user_id] = user.name
                    if hasattr(user, 'description'):
                       users_cache[user_id] += " (" + user.description + ")"


                info = self.get_statistics(instance.id)
                mem =float(info[instance.id]["mem"]["daily"])
                vcpu = float(info[instance.id]["vcpu"]["daily"])

                instance.user = users_cache[user_id]
                instance.memory = mem
                instance.vcpu = vcpu

                my_instances.append(instance)

            elif hasattr(instance, "user_id"):
                 userid = instance.user_id
                 if (userid == os_auth.get_user(self.request).id):
                    my_instances.append(instance)

        return my_instances



class DetailView(TemplateView):
    """
    The monitoring view
    """
    template_name = "project/monitoring/detail.html"
    redirect_url = "horizon:project:monitoring:index"
    page_title = _("Monitoring")

    
    def has_permission(self, request, instance_id):
        """
        Check if user have permission to access instances
        """
        instance = api.nova.server_get(request, instance_id)
        user_id = os_auth.get_user(request).id
        tenant_id = os_auth.get_user(request).project_id
        roles = [str(role["name"]) for role in os_auth.get_user(request).roles]

        if instance.tenant_id == tenant_id and (
            instance.user_id == user_id or settings.PROJECT_MANAGER_ROLE in roles
        ):
            return True
        
        return False


    def get_context_data(self, instance_id, **kwargs):
        """
        Returns the charts
        """
        context = super(DetailView, self).get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["back_to_monitoring_url"] = reverse(self.redirect_url)
        context["is_project_manager"] = helpers.has_role(self.request ,settings.PROJECT_MANAGER_ROLE)

        try:
           if self.has_permission(self.request, instance_id):
              context["page_title"] = instance_id
              
              project_day  = ProjectViewDay()
              project_week = ProjectViewWeek()
              project_hour = ProjectViewHour()

              context["charts_daily"]  = project_day._get_charts_data_daily(instance_id)
              context["charts_weekly"] = project_week._get_charts_data_weekly(instance_id)
              context["charts_hourly"] = project_hour._get_charts_data_hourly(instance_id)
           else:
              raise PermissionsError()

        except PermissionsError:
            msg = _("Insufficient permissions.")
            redirect = reverse(self.redirect_url)
            exceptions.handle(self.request, msg, redirect=redirect)
            
        except Exception:
            msg = _("Unable to retrieve instance monitoring.")
            redirect = reverse(self.redirect_url)
            exceptions.handle(self.request, msg, redirect=redirect)

        return context


    
class ProjectViewHour(TemplateView):
    """
    The hourly statistics
    """
    template_name = "project/monitoring/piecharthour.html"

    def get_context_data(self, instance_id, **kwargs):
        """
        Returns the hourly statistics
        """
        context = super(ProjectViewHour, self).get_context_data(**kwargs)
        context["charts_hourly"] = self._get_charts_data_hourly(instance_id)

        return context


    def get_data(self, instance_id, **kwargs):
        """
        Fetch data from gerenuk API
        """
        gerenuk_config = gerenuk.Config()
        gerenuk_config.load(settings.GERENUK_CONF)
        gerenuk_api = gerenuk.api.InstancesMonitorAPI(gerenuk_config)

        uuid = list()
        uuid.append(str(instance_id))
        results = gerenuk_api.get_instances_monitoring(uuid)

        return results

     
    def _get_charts_data_hourly(self, instance_id):
        """
        Used to extract hourly charts 
        """  
        chart_sections_hourly = []
        for section in CHART_DEFS_HOUR:
            chart_data_hourly = self._process_chart_section_hourly(section["charts_hourly"], instance_id)
            chart_sections_hourly.append({
                "title": section["title"],
                "charts_hourly": chart_data_hourly
            })

        return chart_sections_hourly

     
    def _process_chart_section_hourly(self, chart_defs_hour, instance_id):
        """
        Process the hourly chart section
        """
        charts_hourly = []
        for t in chart_defs_hour:
            uuids_here = instance_id
            key = t.quota_key
            info = self.get_data(instance_id)
            used = float(info[uuids_here][key]["hourly"])
            quota = 100
            text = pgettext_lazy("Label in the limit summary", "Used")
            filters = None
            used_display = None
            quota_display = None

            charts_hourly.append({
                "type": key,
                "name": t.label,
                "used": used,
                "quota": quota,
                "used_display": used_display,
                "quota_display": quota_display,
                "text": text
            })

        return charts_hourly



class ProjectViewDay(TemplateView):
    """
    The daily statistics
    """
    template_name = "project/monitoring/piechartday.html"

    
    def get_context_data(self, instance_id, **kwargs):
        """
        Returns the daily statistics
        """  
        context = super(ProjectViewDay, self).get_context_data(**kwargs)
        context["charts_daily"] = self._get_charts_data_daily(instance_id)

        return context


    def get_data(self, instance_id, **kwargs):
        """
        Returns statistics from Gerenuk
        """
        gerenuk_config = gerenuk.Config()
        gerenuk_config.load(settings.GERENUK_CONF)
        gerenuk_api = gerenuk.api.InstancesMonitorAPI(gerenuk_config)

        uuid = list()
        uuid.append(str(instance_id))
        results = gerenuk_api.get_instances_monitoring(uuid)

        return results

     
    def _get_charts_data_daily(self, instance_id):
        """
        Used to extract daily charts 
        """  
        chart_sections_daily = []
        for section in CHART_DEFS_DAY:
            chart_data_daily = self._process_chart_section_daily(section["charts_daily"], instance_id)
            chart_sections_daily.append({
                "title": section["title"],
                "charts_daily": chart_data_daily
            })

        return chart_sections_daily

     
    def _process_chart_section_daily(self, chart_defs_day, instance_id):
        """
        Process the daily chart section
        """
        charts_daily = []
        for t in chart_defs_day:
            uuids = str(instance_id)
            key = t.quota_key
            info = self.get_data(instance_id)
            used = float(info[uuids][key]["daily"])
            quota = 100
            text = pgettext_lazy("Label in the limit summary", "Used")
            filters = None
            used_display = "daily"
            quota_display = None

            charts_daily.append({
                "type": key,
                "name": t.label,
                "used": used,
                "quota": quota,
                "used_display": used_display,
                "quota_display": quota_display,
                "text": text
            })

        return charts_daily



class ProjectViewWeek(TemplateView):
    """
    The weekly statistics
    """
    template_name = "project/monitoring/piechartweek.html"

    
    def get_context_data(self, instance_id, **kwargs):
        """
        Returns the weekly statistics
        """  
        context = super(ProjectViewWeek, self).get_context_data(**kwargs)
        context["charts_weekly"] = self._get_charts_data_weekly(instance_id)

        return context

     
    def get_data(self, instance_id, **kwargs):
        """
        Returns statistics from Gerenuk
        """
        gerenuk_config = gerenuk.Config()
        gerenuk_config.load(settings.GERENUK_CONF)
        gerenuk_api = gerenuk.api.InstancesMonitorAPI(gerenuk_config)

        uuids = list()
        uuids.append(str(instance_id))
        results = gerenuk_api.get_instances_monitoring(uuids)

        return results

     
    def _get_charts_data_weekly(self, instance_id):
        """
        Get the charts data
        """
        chart_sections_weekly = []
        for section in CHART_DEFS_WEEK:
            chart_data_weekly = self._process_chart_section_weekly(section["charts_weekly"], instance_id)
            chart_sections_weekly.append({
                "title": section["title"],
                "charts_weekly": chart_data_weekly
            })
            
        return chart_sections_weekly

     
    def _process_chart_section_weekly(self, chart_defs_week, instance_id):

        """
        Process and append the statistics 
        """
        charts_weekly = []
        for t in chart_defs_week:
            uuids = str(instance_id)
            key = t.quota_key
            info = self.get_data(instance_id)
            used = float(info[uuids][key]["weekly"])            
            quota = 100
            text = pgettext_lazy("Label in the limit summary", "Used")
            filters = None
            used_display = "weekly"
            quota_display = None

            charts_weekly.append({
                "type": key,
                "name": t.label,
                "used": used,
                "quota": quota,
                "used_display": used_display,
                "quota_display": quota_display,
                "text": text
            })

        return charts_weekly
