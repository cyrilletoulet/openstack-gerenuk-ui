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
# Wed Oct 23 14:10:03 CEST 2019

from django.views.generic import TemplateView
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import api
from openstack_dashboard import policy

### used if version < Rocky ###
#from openstack_dashboard.api import _nova
from openstack_dashboard.api import nova

from openstack_auth import user
from openstack_auth import utils as user_acces


from collections import namedtuple



class AvailableResourcesView(TemplateView):
    """
    The available resources view.
    """

    template_name = "mydashboard/available/flavor.html"


    def get_context_data(self, **kwargs):
        """
        Return the flavor_data context
        """

        context = super(AvailableResourcesView, self).get_context_data(**kwargs)
        context['flavor_data'] = self.get_flavor(self)
        return context


    def get_flavor(self, request):
        """
        Return the available flavors
        """
             
        # _nova used if version < Rocky
        #c = _nova.novaclient(self.request)
        c = nova.novaclient(request)
        hypervisors_list = dict()
            
        flavor_data = dict()
        for h in c.hypervisors.list(): 

            hypervisors_list[h.service["host"]] = h
            aggregates = c.aggregates.list()

            for f in c.flavors.list():

                flavor_meta = f.get_keys()

                if len(flavor_meta.keys()) == 1:
                    flavor_key = flavor_meta.keys()[0]

                    for a in aggregates:
                        if a.name == flavor_key:

                            possible = 0
                            for h in a.hosts:
                                if f.vcpus > (hypervisors_list[h].vcpus - hypervisors_list[h].vcpus_used):
                                    continue
                                if f.ram > hypervisors_list[h].free_ram_mb:
                                    continue
                                if f.disk > hypervisors_list[h].free_disk_gb:
                                    continue

                                tmp = (
                                    hypervisors_list[h].vcpus - hypervisors_list[h].vcpus_used) / f.vcpus
                                tmp = min(
                                    tmp, hypervisors_list[h].free_ram_mb / f.ram)
                                tmp = min(
                                    tmp, hypervisors_list[h].free_disk_gb / f.disk)
                                possible += tmp
                            available = []
                            available.append(possible)
                            for i in poss:
                                flavor_data[i] = f.name
           return flavor_data
