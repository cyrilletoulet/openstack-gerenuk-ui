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
# Mon 21 Oct 15:21:40 CEST 2019

from __future__ import absolute_import
import gerenuk
import datetime
import gerenuk.api
from decimal import Decimal
from collections import defaultdict
import json

from django.template import defaultfilters as filters
from django.template.defaultfilters import yesno
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon.utils import filters
from horizon import tables

from openstack_dashboard import api
from openstack_dashboard.views import get_url_with_pagination
from openstack_auth import utils as user_acces
from openstack_auth.user import User as user_auth
from django.core.handlers.wsgi import WSGIRequest

ROLE = 'project_manager'


class DeleteAlerts(tables.DeleteAction):
   	name = "read" 
    	help_text = _("Deleted alerts are not recoverable.")
    	default_message_level = "info"





    	@staticmethod
    	def action_present(count):
        	return ungettext_lazy(
            	u"Make as read",
            	u"Make as read",
            	count
		)
   
	@staticmethod
	def action_past(count):
		return ungettext_lazy(
            	u"Scheduled deletion of Alert",
      		u"Scheduled deletion of Alert",
            	count
        	)



	def get_object_id(self, datum):
		return datum.id
    

		
	def allowed(self, request, user_alerts=None):
		
		
		req = mydashboard.overview.views.ret(request)
		roles = user_acces.get_user(req).roles
		
		for r in roles :

				if r['name'] == ROLE :
				
					
					
				
                               		return True
	
                return False


                               	

	def delete(self,request, obj_id):
                config = gerenuk.Config()
                config.load('/etc/gerenuk/gerenuk.conf')
                project = "75a5d7351c6c4a40ad9fc3ab0a50f4d0"
		
                api = gerenuk.api.AlertsAPI(config)
                unread_alerts = api.get_unread_alerts(project)
	        read_ids = list()
		for i in range(0, min(1,len(unread_alerts))):
	 	  	
		    print ("in the verify") 
        	    read_ids.append(unread_alerts[i]["id"])
		
		api.tag_alerts_as_read([int(obj_id)])
		print("\n")
		
		print ("Delete in PM Section Done")
	




















class DeleteAlertsUser(tables.DeleteAction):
   	name = "read" 
    	help_text = _("Deleted alerts are not recoverable.")
    	default_message_level = "info"





    	@staticmethod
    	def action_present(count):
        	return ungettext_lazy(
            	u"Make as read",
            	u"Make as read",
            	count
		)
   
	@staticmethod
	def action_past(count):
		return ungettext_lazy(
            	u"Scheduled deletion of Alert",
      		u"Scheduled deletion of Alert",
            	count
        	)



	def get_object_id(self, datum):
		return datum.id
    
	def delete(self,request, obj_id):
                config = gerenuk.Config()
                config.load('/etc/gerenuk/gerenuk.conf')
                project = "75a5d7351c6c4a40ad9fc3ab0a50f4d0"
		
                api = gerenuk.api.AlertsAPI(config)
                unread_alerts = api.get_unread_alerts(project)
	        read_ids = list()
		for i in range(0, min(1,len(unread_alerts))):
	 	  	
		    print ("in the verify") 
        	    read_ids.append(unread_alerts[i]["id"])
		
		
		api.tag_alerts_as_read([int(obj_id)])
		print("\n")
		
		print ("Delete in User Section Done")
	






SEVERITY = {
	 	0: "INFO", 
		1: "ALERT", 
		2: "WARNING",
		3: "CRITICAL",
	   }

SEVERITY_CHOICES = (
	 ("INFO","Info"),
         ("ALERT","Alert"),
         ("WARNING","Warning"),
         ("CRITICAL","Critical"),
	)
def get_severity(alert_named):
	
	return SEVERITY.get(getattr(alert_named, "severity",0), '')

	
        


class AlertsTable(tables.DataTable):




	project = tables.Column("project", verbose_name=_("Project"))
	
        
#        zone = tables.Column('availability_zone',
 #                             verbose_name=_("Availability Zone"))
        message_fr = tables.Column('message_fr', verbose_name=_("Message"))
	
        id = tables.Column('id', verbose_name=_("Id "))

        severity = tables.Column(get_severity, verbose_name=_("Severity"),
				sortable= True,
				display_choices=SEVERITY_CHOICES)


	created = tables.Column("timestamp" , verbose_name=_("Created "))



 	def get_object_id(self, datum):
		return datum.id
	   

        class Meta(object):
            name = "alerts"
            verbose_name = _("Alerts")
	    status_columns = ["severity",]
            table_actions = (DeleteAlerts,)
	    row_actions = (DeleteAlerts,)


class AlertsEnTable(tables.DataTable):




        project = tables.Column("project", verbose_name=_("Project"))


#        zone = tables.Column('availability_zone',
 #                             verbose_name=_("Availability Zone"))
        message_en = tables.Column('message_en', verbose_name=_("Message"))

        id = tables.Column('id', verbose_name=_("Id "))

        severity = tables.Column(get_severity, verbose_name=_("Severity"),
                                sortable= True,
                                display_choices=SEVERITY_CHOICES)


        created = tables.Column("timestamp" , verbose_name=_("Created "))



        def get_object_id(self, datum):
                return datum.id


        class Meta(object):
            name = "alerts_en"
            verbose_name = _("Alerts")
            status_columns = ["severity",]
            table_actions = (DeleteAlerts,)
            row_actions = (DeleteAlerts,)




    
class UserTable(tables.DataTable):




        uuid = tables.Column("uuid", verbose_name=_("User's ID"))

        message_fr = tables.Column('message_fr', verbose_name=_("Message"))

        id = tables.Column('id', verbose_name=_("Id "))

        severity = tables.Column(get_severity, verbose_name=_("Severity"),
                                sortable= True,
                                display_choices=SEVERITY_CHOICES)


        created = tables.Column("timestamp" , verbose_name=_("Created "))



        def get_object_id(self, datum):
                return datum.id


        class Meta(object):
            name = "user"
            verbose_name = _("User Alerts")
            status_columns = ["severity",]
            table_actions = (DeleteAlertsUser,)
            row_actions = ( DeleteAlertsUser,)

class UserEnTable(tables.DataTable):




        uuid = tables.Column("uuid", verbose_name=_("User's ID"))

        message_en = tables.Column('message_en', verbose_name=_("Message"))

        id = tables.Column('id', verbose_name=_("Id "))

        severity = tables.Column(get_severity, verbose_name=_("Severity"),
                                sortable= True,
                                display_choices=SEVERITY_CHOICES)


        created = tables.Column("timestamp" , verbose_name=_("Created "))



        def get_object_id(self, datum):
                return datum.id


        class Meta(object):
            name = "user_en"
            verbose_name = _("User Alerts")
            status_columns = ["severity",]
            table_actions = (DeleteAlertsUser,)
            row_actions = ( DeleteAlertsUser,)



