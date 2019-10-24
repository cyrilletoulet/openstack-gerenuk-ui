# -*- coding: utf-8 -*-
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
# Thu 24 Oct 16:37:51 CEST 2019

from django.utils.translation import ugettext_lazy as _
from horizon import tables


class AvailableResourcesTable(tables.DataTable):
    """
    The horizon table used to display available resources.
    """
    id = tables.Column('id', verbose_name=_("Flavor id"))
    name = tables.Column("name", verbose_name=_("Flavor name"))
    available = tables.Column("available", verbose_name=_("Available instances"))


    class Meta(object):
        """
        Define metadata.
        """
        name = "flavors"
        verbose_name = _("Flavors")
        columns = ('id', 'name', 'available')
