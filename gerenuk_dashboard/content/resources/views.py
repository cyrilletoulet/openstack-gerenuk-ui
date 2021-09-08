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
# Wed Sep  8 03:16:03 PM CEST 2021

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
    The user resources view.
    """
    table_classes = (
        tables.InstancesTable,
        tables.VolumesTable,
        tables.SnapshotsTable
    )
    template_name = "project/resources/index.html"
    page_title = _("My resources")
    users_cache = dict()

    
    def cache_user(self, user_id):
        """
        Add an user to the users cache if not exists
        :param user_id: (str) The user id to cache
        """
        if not user_id in self.users_cache:
            try:
                user = api.keystone.user_get(self.request, user_id, admin=False)
                self.users_cache[user_id] = user.name
                if hasattr(user, 'description'):
                    self.users_cache[user_id] += " (" + user.description + ")"
            except:
                self.users_cache[user_id] = "Deleted (%s)" % (user_id,)


    def get_context_data(self, **kwargs):
        """
        Define the view context
        """
        context = super(IndexView, self).get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["all_resources_url"] = reverse("horizon:project:resources:all")
        context["is_project_manager"] = helpers.has_role(self.request ,settings.PROJECT_MANAGER_ROLE)
        return context


    def get_instances_data(self):
        """
        Getter used by InstancesTable model.
        """
        user_id = os_auth.get_user(self.request).id
        self.cache_user(user_id)
        
        instances_list = []
        instances, self._more = api.nova.server_list(self.request)

        for instance in instances:
            if hasattr(instance, "user_id"):
                if (user_id == instance.user_id):
                    instance.user = self.users_cache[user_id]
                    instances_list.append(instance)

        return instances_list


    def get_volumes_data(self):
        """
        Getter used by VolumesTable model.
        """
        user_id = os_auth.get_user(self.request).id
        self.cache_user(user_id)
        filters = {"user_id": user_id}

        cinder = api.cinder.cinderclient(self.request)
        unfiltred_volumes = cinder.volumes.list()
        volumes_list = list()

        for volume in unfiltred_volumes:
            if all(getattr(volume, attr) == value for (attr, value) in filters.items()):
                volume.user = self.users_cache[user_id]
                volumes_list.append(volume)

        return volumes_list

    
    def get_snapshots_data(self):
        """
        Getter used by SnapshotsTable model.
        """
        user_id = os_auth.get_user(self.request).id
        self.cache_user(user_id)
        owner = os_auth.get_user(self.request).project_id
        filters = {"owner" : owner}
        
        snapshots_list = list()

        try:
            snapshots = api.glance.image_list_detailed(self.request)
            for snapshot in snapshots[0]:
                if snapshot.properties.get("image_type") == "snapshot":
                    if (
                            all(getattr(snapshot, attr) == value for (attr, value) in filters.items())
                            and snapshot.properties.get("user_id") == user_id
                    ):
                        snapshot.user = self.users_cache[user_id]
                        snapshots_list.append(snapshot)

            return snapshots_list

        except Exception:
            snapshots_list = []
            exceptions.handle(self.request,_("Unable to retrieve snapshots"))





class AllResourcesView(MultiTableView):
    """
    The project resources view.
    """
    table_classes = (
        tables.InstancesTable,
        tables.VolumesTable,
        tables.SnapshotsTable
    )
    template_name = "project/resources/all.html"
    page_title = _("All users resources")
    users_cache = dict()

    
    def cache_user(self, user_id):
        """
        Add an user to the users cache if not exists
        :param user_id: (str) The user id to cache
        """
        if not user_id in self.users_cache:
            try:
                user = api.keystone.user_get(self.request, user_id, admin=False)
                self.users_cache[user_id] = user.name
                if hasattr(user, 'description'):
                    self.users_cache[user_id] += " (" + user.description + ")"
            except:
                self.users_cache[user_id] = "Deleted (%s)" % (user_id,)


    def get_context_data(self, **kwargs):
        """
        Define the view context
        """
        context = super(AllResourcesView, self).get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["back_to_resources_url"] = reverse("horizon:project:resources:index")
        context["is_project_manager"] = helpers.has_role(self.request ,settings.PROJECT_MANAGER_ROLE)
        return context


    def get_instances_data(self):
        """
        Getter used by InstancesTable model.
        """
        instances_list = []
        instances, self._more = api.nova.server_list(self.request)

        for instance in instances:
            if helpers.has_role(self.request, settings.PROJECT_MANAGER_ROLE):
                user_id = instance.user_id
                self.cache_user(user_id)
                instance.user = self.users_cache[user_id]
                instances_list.append(instance)

        return instances_list


    def get_volumes_data(self):
        """
        Getter used by VolumesTable model.
        """
        cinder = api.cinder.cinderclient(self.request)
        unfiltred_volumes = cinder.volumes.list()
        volumes_list = list()

        for volume in unfiltred_volumes:
            if helpers.has_role(self.request, settings.PROJECT_MANAGER_ROLE):
                user_id = volume.user_id
                self.cache_user(user_id)
                volume.user = self.users_cache[user_id]
                volumes_list.append(volume)

        return volumes_list

    
    def get_snapshots_data(self):
        """
        Getter used by SnapshotsTable model.
        """
        owner = os_auth.get_user(self.request).project_id
        filters = {"owner" : owner}
        snapshots_list = list()

        try:
            snapshots = api.glance.image_list_detailed(self.request)

            for snapshot in snapshots[0]:
                if snapshot.properties.get("image_type") == "snapshot":
                    if (
                            all(getattr(snapshot, attr) == value for (attr, value) in filters.items())
                            and helpers.has_role(self.request, settings.PROJECT_MANAGER_ROLE)
                    ):
                        user_id = snapshot.properties.get("user_id")
                        self.cache_user(user_id)
                        snapshot.user = self.users_cache[user_id]
                        snapshots_list.append(snapshot)

            return snapshots_list

        except Exception:
            snapshots_list = []
            exceptions.handle(self.request,_("Unable to retrieve snapshots"))
