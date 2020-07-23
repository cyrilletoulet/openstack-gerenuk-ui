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
# Thu 23 Jul 15:21:04 CEST 2020

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
    page_title = _("Available resources")


    def get_context_data(self, **kwargs):
        """
        Return the view context
        """
        context = super(AvailableResourcesView, self).get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["flavors_availability"] = self.get_flavors_availability(self)
        context["is_project_manager"] = helpers.has_role(self.request ,settings.PROJECT_MANAGER_ROLE)
        return context


    def get_flavors_availability(self, request):
        """
        Return the available flavors
        """
        try:
            # Until Stein release
            nova_client = nova.novaclient(self.request)
        except:
            # From Stein release
            nova_client = nova
        
        hypervisors_list = dict()
        flavors_availability = dict()

        try:
            # Until Stein release
            for hypervisor in nova_client.hypervisors.list(): 
                hypervisors_list[hypervisor.service["host"]] = hypervisor
            aggregates = nova_client.aggregates.list()
        except:
            # From Stein release
            for hypervisor in nova_client.hypervisor_list(self.request):
                hypervisors_list[hypervisor.service["host"]] = hypervisor
            aggregates = nova_client.aggregate_details_list(self.request)

        try:
            # Until Stein release
            flavor_list = nova_client.flavors.list()
        except:
            # From Stein release
            flavor_list = nova_client.flavor_list(self.request)
            
        for flavor in flavor_list:
                flavor_meta = flavor.get_keys()
                
                if len(flavor_meta.keys()) >= 1:
                    for aggregate in aggregates:
                        if aggregate.name in flavor_meta.keys():
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

                            flavors_availability[flavor.name] = possible
                                
        return flavors_availability
