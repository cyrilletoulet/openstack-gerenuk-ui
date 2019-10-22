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
# Tue 22 Oct 09:40:27 CEST 2019

from django.utils.translation import ugettext_lazy as _


# The slug of the dashboard the PANEL associated with
PANEL_DASHBOARD = 'project'

# The slug of the panel group the PANEL is associated with
PANEL_GROUP = 'information'

# The slug of the panel to be added to HORIZON_CONFIG
PANEL = 'alerts'

# Python panel class of the PANEL to be added
ADD_PANEL = 'gerenuk_dashboard.content.alerts.panel.Alerts'

# Automatically discover static resources in installed apps
AUTO_DISCOVER_STATIC_FILES = True
