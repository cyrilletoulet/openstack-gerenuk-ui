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
# Fri 25 Oct 09:39:03 CEST 2019

from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables

from openstack_dashboard import api
from openstack_dashboard.views import get_url_with_pagination


def get_monitoring_detail_link(obj, request):
    """
    Redirects to monitoring details
    """
    return get_url_with_pagination(
        request,
        InstancesTable._meta.pagination_param,
        InstancesTable._meta.prev_pagination_param,
        'horizon:project:monitoring:detail',
        obj.id
    )

def get_instance_detail_link(obj, request):
    """
    Redirects to instance details
    """
    return get_url_with_pagination(
        request,
        InstancesTable._meta.pagination_param,
        InstancesTable._meta.prev_pagination_param,
        'horizon:project:instances:detail',
        obj.id
    )



class InstancesTable(tables.DataTable):
    """
    The horizon table used to display instance.
    """
    def get_instid(instance):
        """
        Get instance id.
        """
        if hasattr(instance, "id"):
            instid = instance.id
        return instid


    name = tables.Column("name", verbose_name=_("Name"), link=get_instnace_detail_link)
    instance_id = tables.Column(get_instid, verbose_name=_("Statistics"), link=get_monitoring_detail_link)
    image_name = tables.Column('image_name', verbose_name=_("Image"))
    status = tables.Column("status", verbose_name=_("Status"))


    class Meta(object):
        """
        Define metadata.
        """
        name = "instances"
        verbose_name = _("Instances")
        status_columns = ["status",]
