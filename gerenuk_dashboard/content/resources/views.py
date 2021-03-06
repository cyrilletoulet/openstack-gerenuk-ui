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
# Fri 14 Feb 13:30:55 CET 2020

from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.conf import settings

from horizon.tables import MultiTableView
from horizon import exceptions
from horizon import messages

from gerenuk_dashboard.content.resources import tables
from gerenuk_dashboard.content import helpers
from openstack_dashboard import api
from openstack_auth import utils as os_auth

from collections import OrderedDict as SortedDict

import gerenuk



class IndexView(MultiTableView):
    """
    The resources view.
    """
    table_classes = (
        tables.InstancesTable,
        tables.VolumesTable,
        tables.SnapshotsTable
    )
    template_name = "project/resources/index.html"
    page_title = _("Resources")


    def get_context_data(self, **kwargs):
        """
        Define the view context
        """
        context = super(IndexView, self).get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["instances_url"] = reverse("horizon:project:instances:index")
        context["volumes_url"] = reverse("horizon:project:volumes:index")
        context["is_project_manager"] = helpers.has_role(self.request ,settings.PROJECT_MANAGER_ROLE)
        return context


    def get_instances_data(self):
        """
        Getter used by InstancesTable model.
        """
        instances_list = []
        instances, self._more = api.nova.server_list(self.request)

        for i in instances:
            if hasattr(i, "user_id"):
                userid = i.user_id
                if (userid == os_auth.get_user(self.request).id):
                    instances_list.append(i)

        return instances_list


    def get_volumes_data(self):
        """
        Getter used by VolumesTable model.
        """
        userid = os_auth.get_user(self.request).id
        filters = {"user_id": userid}

        cinder = api.cinder.cinderclient(self.request)
        unfiltred_volumes = cinder.volumes.list()
        volumes_list = list()

        for volume in unfiltred_volumes:
            if all(getattr(volume, attr) == value for (attr, value) in filters.items()):
                volumes_list.append(volume)

        return volumes_list

    def get_snapshots_data(self):
        """
        Getter used by SnapshotsTable model.
        """
        userid = os_auth.get_user(self.request).id
        owner = os_auth.get_user(self.request).project_id
        filters = {"owner" : owner}
        snapshots_list = list()
        users_cache = dict()

        try:
            snapshots = api.glance.image_list_detailed(self.request)
            for snapshot in snapshots[0]:
                if snapshot.properties.get("image_type") == "snapshot":
                    if (snapshot.properties.get("user_id") == userid) or all(
                            getattr(snapshot, attr) == value for (attr, value) in filters.items()
                    ) and helpers.has_role(self.request, settings.PROJECT_MANAGER_ROLE):
                        user_id = snapshot.properties.get("user_id")
                        if not user_id in users_cache:
                            try:
                                user = api.keystone.user_get(self.request, user_id, admin=False)
                                users_cache[user_id] = user.name
                                if hasattr(user, 'description'):
                                    users_cache[user_id] += " (" + user.description + ")"
                            except:
                                users_cache[user_id] = "Deleted (%s)" % (user_id,)

                        snapshot.user = users_cache[user_id]
                        snapshots_list.append(snapshot)

            return snapshots_list

        except Exception:
            snapshots_list = []
            exceptions.handle(self.request,_("Unable to retrieve snapshots"))
