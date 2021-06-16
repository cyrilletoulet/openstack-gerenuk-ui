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
# Wed Jun 16 10:19:55 AM CEST 2021

from django.conf.urls import url
from gerenuk_dashboard.content.resources import views


# Define URL patterns
urlpatterns = [
    url(r"^$", views.IndexView.as_view(), name="index"),
    url(r"^all/$", views.AllResourcesView.as_view(), name="all"),
]
