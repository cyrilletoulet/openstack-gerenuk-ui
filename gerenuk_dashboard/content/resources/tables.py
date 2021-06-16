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
# Wed 18 Dec 14:10:42 CET 2019

from django.conf import settings
from django.template import defaultfilters as filters
from django.urls import reverse
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import tables

from openstack_dashboard import api
from openstack_dashboard.views import get_url_with_pagination


# Constants
STATUS_CHOICES = (
    ("in-use", True),
    ("available", True),
    ("creating", None),
    ("error", False),
    ("error_extending", False),
)

TYPE_CHOICES = (
    ("snapshot", pgettext_lazy("Type of an image", u"Snapshot")),
    ("image", pgettext_lazy("Type of an image", u"Image")),
)


# Functions
def get_server_detail_link(obj, request):
    """
    Redirection to instance details
    """
    return get_url_with_pagination(
        request,
        InstancesTable._meta.pagination_param,
        InstancesTable._meta.prev_pagination_param,
        "horizon:project:instances:detail", 
        obj.id
    )


def get_monitoring_detail_link(obj, request):
    """
    Redirection to monitoring details
    """
    return get_url_with_pagination(
        request,
        InstancesTable._meta.pagination_param,
        InstancesTable._meta.prev_pagination_param,
        "horizon:project:monitoring:detail", 
        obj.id
    )


def get_instance_id(instance):
    """
    Get instnace id.
    """
    if hasattr(instance, "id"):
       return instance.id
   
    return _("Not available")


def get_volume_project_id(volume):
    """
    Get volume tenant id.
    """
    if hasattr(volume, "id"):
        return volume.id
    
    return _("Not available")


def get_volume_size(volume):
    """
    Get volume size.
    """
    return _("%sGB") % volume.size


def get_snapshot_id(image):
    """
    Get snapshot id.
    """
    if hasattr(image, "id"):
        return image.id
    
    return _("Not available")


def get_image_type(image):
    """
    Get image/snapshot type.
    """
    if image.properties.get("image_type") == "snapshot":
        return "snapshot"


def get_snapshot_name(image):
    """
    Get snapshot name.
    """
    return getattr(image, "name", None) or image.id


# Classes
class InstancesTable(tables.DataTable):
    """
    The horizon table used to display user instances.
    """
    owner = tables.Column("user", verbose_name=_("User"))
    name = tables.Column("name", verbose_name=_("Name"), link=get_server_detail_link)
    status = tables.Column("status", verbose_name=_("Status"))
    image_name = tables.Column("image_name", verbose_name=_("Image name"))
    instance_id = tables.Column(get_instance_id, verbose_name=_("Instance monitoring"), link=get_monitoring_detail_link)


    class Meta(object):
        """
        Define metadata.
        """
        name = "instances"
        verbose_name = _("Instances")
        status_columns = ["status"]



class VolumesTable(tables.DataTable):
    """
    The horizon table used to display user volumes.
    """
    owner = tables.Column("user", verbose_name=_("User"))
    name = tables.Column("name", verbose_name=_("Name"),link="horizon:project:volumes:detail")
    description = tables.Column("description", verbose_name=_("Description"))
    size = tables.Column(get_volume_size, verbose_name=_("Size"), attrs={"data-type": "size"})
    status = tables.Column("status", filters=(filters.title,),verbose_name=_("Status"),status=True,status_choices=STATUS_CHOICES)
    project = tables.Column(get_volume_project_id, verbose_name=_("ID"))


    def get_object_display(self, obj):
        return obj.name


    class Meta:
        """
        Define metadata.
        """
        name = "volumes"
        verbose_name = _("Volumes")
        status_columns = ["status"]



class SnapshotsTable(tables.DataTable):
    """
    The horizon table used to display snapshots.
    """
    owner = tables.Column("user", verbose_name=_("User"))
    name = tables.WrappingColumn(get_snapshot_name, verbose_name=_("Snapshot Name"),link="horizon:project:images:images:detail")
    description = tables.Column("description",verbose_name=_("Description"))
    snapshot_type = tables.Column(get_image_type, verbose_name=_("Type"), display_choices=TYPE_CHOICES)
    snapshot_id= tables.Column(get_snapshot_id,verbose_name=_("Snapshot ID"))


    class Meta(object):
        """
        Define metadata.
        """
        name = "snapshots"
        verbose_name = _("Snapshots")
