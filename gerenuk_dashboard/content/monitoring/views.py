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
# 

from openstack_dashboard.dashboards.mydashboard.monitoring import tables
from horizon import tables

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy

from horizon import exceptions

from openstack_dashboard import api
from openstack_auth import utils as user_acces


import gerenuk

import collections
from django.views.generic import TemplateView





ChartDefHour = collections.namedtuple(
    'ChartDefHour',
    ('quota_key', 'label', 'used_phrase', 'filters'))

CHART_DEFS_HOUR = [
    {
        'title': _("Monitoring Hourly"),
        'charts_hourly': [
            ChartDefHour("mem", _("Memory"), None, None),
            ChartDefHour("vcpu", _("Vcpu"), None, None),
            ChartDefHour("cpu", _("CPU"), None, None),

        ]
    }]


ChartDefWeek = collections.namedtuple(
    'ChartDefHour',
    ('quota_key', 'label', 'used_phrase', 'filters'))

CHART_DEFS_WEEK = [
    {
        'title': _("Monitoring Weekly"),
        'charts_weekly': [
            ChartDefHour("mem", _("Memory"), None, None),
            ChartDefHour("vcpu", _("Vcpu"), None, None),
            ChartDefHour("cpu", _("CPU"), None, None),

        ]
    }]


ChartDefDay = collections.namedtuple(
    'ChartDefDay',
    ('quota_key', 'label', 'used_phrase', 'filters'))

CHART_DEFS_DAY = [
    {
        'title': _("Monitoring Daily"),
        'charts_daily': [
            ChartDefDay("mem", _("Memory"), None, None),
            ChartDefDay("vcpu", _("Vcpu"), None, None),
            ChartDefDay("cpu", _("CPU"), None, None),

        ]
    }]





class IndexView(tables.DataTableView):
   """
   The instances view  
   """

   table_class = project_tables.InstancesTable
   template_name = 'mydashboard/monitoring/index.html'
   page_title = _("Monitoring")

    def has_role(self, name):
        """
        Check if the current user has a given role
        """
        roles = user_acces.get_user(self.request).roles

        for r in roles:
            if r['name'] == name :
                return True

        return False


    def get_data(self):
        """
        Getter used by the InstancesTable model
        """

        my_instances = []

        instances, self._more = api.nova.server_list(self.request)
        
        for instance in instances:

            if self.verify(ROLE):

                my_instances.append(instance)

            elif hasattr(instance, 'user_id'):
                 userid = instance.user_id
                 if (userid == user_acces.get_user(self.request).id):
                    my_instances.append(instance)

                 else:
                    msg = _('Unable to retrieve instance size information.')
                    exceptions.handle(self.request, msg)
       
        return my_instances


############################################
####            MONITORING              ####
############################################

class DetailView(TemplateView):

    """
    The monitoring view
    """

    template_name = "mydashboard/monitoring/detail.html"
    redirect_url = 'horizon:mydashboard:monitoring:index'
    page_title = "{{ instance.name }}"

    def get_context_data(self, instance_id, **kwargs):
        """
        Returns the charts
        """
        project_day  = ProjectViewDay()
        project_week = ProjectViewWeek()
        project_hour = ProjectViewHour()

        context = project_hour.get_context_data(instance_id, **kwargs)
        context = project_day.get_context_data(instance_id, **kwargs)
        context = project_week.get_context_data(instance_id, **kwargs)

        context['charts_daily']  = project_day._get_charts_data_daily(instance_id)
        context['charts_weekly'] = project_week._get_charts_data_weekly(instance_id)
        context['charts_hourly'] = project_hour._get_charts_data_hourly(instance_id)

        return context


########### HOURLY ##########

class ProjectViewHour(TemplateView):
    """
    The hourly statistics
    """


    template_name = "mydashboard/monitoring/piecharthour.html"

    def get_context_data(self, instance_id, **kwargs):
        """
        Returns the hourly statistics
        """
        context = super(ProjectViewHour, self).get_context_data(**kwargs)
        context['charts_hourly'] = self._get_charts_data_hourly(instance_id)

        return context


    def get_data(self, instance_id, **kwargs):

        gerenuk_config = gerenuk.Config()
        gerenuk_config.load(settings.GERENUK_CONF)
        gerenuk_api = gerenuk.api.AlertsAPI(gerenuk_config)


        uuid = list()
        uuid.append(str(instance_id))
        results = api.get_instances_monitoring(uuid)

        return results

    def _get_charts_data_hourly(self, instance_id):
        """
         User to extract hourly charts 
        """  

        chart_sections_hourly = []
        for section in CHART_DEFS_HOUR:

            chart_data_hourly = self._process_chart_section_hourly(section['charts_hourly'], instance_id)
            chart_sections_hourly.append({
                'title': section['title'],
                'charts_hourly': chart_data_hourly
            })

        return chart_sections_hourly

    def _process_chart_section_hourly(self, chart_defs_hour, instance_id):
        charts_hourly = []
        for t in chart_defs_hour:

            uuids_here = instance_id

            key = t.quota_key
            info = self.get_data(instance_id)
            used = float(info[uuids_here][key]['hourly'])
            quota = (100 - used)
            text = pgettext_lazy('Label in the limit summary', 'Used')
            filters = None
            used_display = None
            quota_display = None

            charts_hourly.append({
                'type': key,
                'name': t.label,
                'used': used,
                'quota': quota,
                'used_display': used_display,
                'quota_display': quota_display,
                'text': text
            })

        return charts_hourly


########### DAILY ##########

class ProjectViewDay(TemplateView):

    template_name = "mydashboard/monitoring/piechartday.html"

    def get_data(self, instance_id, **kwargs):
        
        gerenuk_config = gerenuk.Config()
        gerenuk_config.load(settings.GERENUK_CONF)
        gerenuk_api = gerenuk.api.AlertsAPI(gerenuk_config)

        uuid = list()
        uuid.append(str(instance_id))
        results = api.get_instances_monitoring(uuid)

        return results

    def _get_charts_data_daily(self, instance_id):
        chart_sections_daily = []
        for section in CHART_DEFS_DAY:
            chart_data_daily = self._process_chart_section_daily(
                section['charts_daily'], instance_id)
            chart_sections_daily.append({
                'title': section['title'],
                'charts_daily': chart_data_daily
            })
        return chart_sections_daily

    def _process_chart_section_daily(self, chart_defs_day, instance_id):
        charts_daily = []
        for t in chart_defs_day:

            #            uuids = "435400fe-f40c-4af8-af99-f53f8db3357c"
            uuids = str(instance_id)
            key = t.quota_key
        #    print key
            info = self.get_data(instance_id)
            used = float(info[uuids][key]['daily'])

            quota = (100 - used)
 #   print quota
            text = pgettext_lazy('Label in the limit summary', 'Used')
            filters = None

            used_display = "daily"
            # When quota is float('inf'), we don't show quota
            # so filtering is unnecessary.
            quota_display = None

            charts_daily.append({
                'type': key,
                'name': t.label,
                'used': used,
                'quota': quota,
                'used_display': used_display,
                'quota_display': quota_display,
                'text': text
            })

        return charts_daily

    def get_context_data(self, instance_id, **kwargs):
        context = super(ProjectViewDay, self).get_context_data(**kwargs)

        context['charts_daily'] = self._get_charts_data_daily(instance_id)

        #context = Context(context1, context2)
        return context


# WEEKLY ############"


class ProjectViewWeek(TemplateView):

    template_name = "mydashboard/monitoring/piechartweek.html"

    def get_data(self, instance_id, **kwargs):
        config = gerenuk.Config()
        config.load('/etc/gerenuk/gerenuk.conf')
        stats = []
        api = gerenuk.api.InstancesMonitorAPI(config)
        #uuids = ["435400fe-f40c-4af8-af99-f53f8db3357c"]
        uuids = list()
        uuids.append(str(instance_id))
        results = api.get_instances_monitoring(uuids)
        return results

    def _get_charts_data_weekly(self, instance_id):
        chart_sections_weekly = []
        for section in CHART_DEFS_WEEK:
            chart_data_weekly = self._process_chart_section_weekly(
                section['charts_weekly'], instance_id)
            chart_sections_weekly.append({
                'title': section['title'],
                'charts_weekly': chart_data_weekly
            })
        return chart_sections_weekly

    def _process_chart_section_weekly(self, chart_defs_week, instance_id):
        charts_weekly = []
        for t in chart_defs_week:

            #            uuids = "435400fe-f40c-4af8-af99-f53f8db3357c"
            uuids = str(instance_id)
            key = t.quota_key
            #  print key
            info = self.get_data(instance_id)
            used = float(info[uuids][key]['weekly'])
            #print ("this is the used weekly")
           # print used
            quota = (100 - used)
            # print quota
            text = pgettext_lazy('Label in the limit summary', 'Used')
            filters = None

            used_display = "weekly"
            # When quota is float('inf'), we don't show quota
            # so filtering is unnecessary.
            quota_display = None

            charts_weekly.append({
                'type': key,
                'name': t.label,
                'used': used,
                'quota': quota,
                'used_display': used_display,
                'quota_display': quota_display,
                'text': text
            })

        return charts_weekly

    def get_context_data(self, instance_id, **kwargs):
        context = super(ProjectViewWeek, self).get_context_data(**kwargs)
        context['charts_weekly'] = self._get_charts_data_weekly(instance_id)
        return context

