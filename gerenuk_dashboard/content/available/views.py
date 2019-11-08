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
# Fri  8 Nov 08:45:13 CET 2019

from django.views.generic import TemplateView
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from openstack_auth import user
from openstack_dashboard import api
from openstack_dashboard import policy
from openstack_dashboard.api import nova

from gerenuk_dashboard.content import helpers

from collections import namedtuple


class AvailableResourcesView(TemplateView):
    """
    The available resources view.
    """
    template_name = "project/available/index.html"
    page_title = _("Avaialble resources")


    def get_context_data(self, **kwargs):
        """
        Return the flavor_data context
        """
        context = super(AvailableResourcesView, self).get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["flavor_data"] = self.get_flavor(self)
        context["is_project_manager"] = helpers.has_role(self.request ,settings.PROJECT_MANAGER_ROLE)
        return context


    def get_flavor(self, request):
        """
        Return the available flavors
        """
        nova_client = nova.novaclient(self.request)
        hypervisors_list = dict()
        flavor_data = dict()

        for hypervisor in nova_client.hypervisors.list(): 
            hypervisors_list[hypervisor.service["host"]] = hypervisor
        aggregates = nova_client.aggregates.list()

        for flavor in nova_client.flavors.list():
                flavor_meta = flavor.get_keys()
                
                if len(flavor_meta.keys()) == 1:
                    flavor_key = flavor_meta.keys()[0]

                    for aggregate in aggregates:
                        if aggregate.name == flavor_key:
                            possible = 0
                            for aggregate_host in aggregate.hosts:
                                if flavor.vcpus > (hypervisors_list[aggregate_host].vcpus - hypervisors_list[aggregate_host].vcpus_used):
                                    continue
                                if flavor.ram > hypervisors_list[aggregate_host].free_ram_mb:
                                    continue
                                if flavor.disk > hypervisors_list[aggregate_host].free_disk_gb:
                                    continue

                                tmp = (hypervisors_list[aggregate_host].vcpus - hypervisors_list[aggregate_host].vcpus_used) / flavor.vcpus
                                tmp = min(tmp, hypervisors_list[aggregate_host].free_ram_mb / flavor.ram)
                                tmp = min(tmp, hypervisors_list[aggregate_host].free_disk_gb / flavor.disk)
                                possible += tmp

                            available = []
                            available.append(possible)

                            for i in available:
                                flavor_data[i] = flavor.name
                                
        return flavor_data
