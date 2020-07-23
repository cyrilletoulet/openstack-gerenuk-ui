# The OpenStack Gerenuk UI

This UI is a dashboard extension for Horizon project.

## Build distribution tarball

To build a distribution tarball:
```bash
python setup.py sdist
```

The distribution will be located in **dist/** directory.


## Installation
### Prerequisites

First of all, you need to install [gerenuk](https://github.com/cyrilletoulet/gerenuk) API. 
Please refer to the Gerenuk documentation for details.

First, install gerenuk package:
```bash
yum-config-manager --enable epel
yum -y install python-pip mysql-connector-python
yum-config-manager --disable epel
pip install gerenuk-1.4.0.tar.gz
mkdir /etc/gerenuk
chmod -R 711 /etc/gerenuk
touch /etc/gerenuk/gerenuk.conf
chmod 644 /etc/gerenuk/gerenuk.conf
```

Next, configure gerenuk in **/etc/gerenuk/gerenuk.conf**:
```
[database]
db_host = controller.domain
db_name = gerenuk
db_user = gerenuk_dashboard
db_pass = *secret*
```
*Don't forget to allow port 3306 from the dashobard to the cloud controller in firewall!*

Configure the gerenuk dashboard in horizon settings (**/etc/openstack-dashboard/local_settings**):
```
# Gerenuk dashboard configuration
GERENUK_CONF = "/etc/gerenuk/gerenuk.conf"
PROJECT_MANAGER_ROLE = "project_manager"
```

Finally, configure the OpenStack API policies to add the project manager role:
```
# In /etc/keystone/policy.json
    "project_manager": "role:project_manager",
    "identity:get_user": "rule:admin_or_owner or rule:project_manager",

# In /etc/nova/policy.json
    "project_manager": "role:project_manager and project_id:%(project_id)s",
    "default": "rule:admin_or_user or rule:project_manager",
    "os_compute_api:os-hypervisors": "rule:default",
```

And restart the concerned APIs:
```bash
systemctl restart openstack-nova-api.service httpd.service
```


### Dashboard extension

Install the openstack-gerenuk-ui by copying python package:
```bash
pip install gerenuk_dashboard-2.0.tar.gz
cp /usr/lib/python2.7/site-packages/gerenuk_dashboard/enabled/* /usr/share/openstack-dashboard/openstack_dashboard/local/enabled/
```

And finally restart the HTTP server:
```bash
systemctl restart httpd
```

You should now find the new dashboard in **Project** / **Information** panel.


## Configuration

To use the "Available resources" panel, the nova "Host Aggregate" name has to be present in corresponding flavor metadatas.


## Development
### Translation

To update the translation files, you need to deploy your code on a development server.

First, you can generate the language file:
```bash
cd /usr/lib/python2.7/site-packages/gerenuk_dashboard/
django-admin makemessages -l fr 
```

Next, download the *.po* file generated in **locale/fr/LC_MESSAGES/django.po**.
This file contains all the sentences to translate.

You can translate it manually or using a tool like [Zanata](https://translate.zanata.org/) (after changing the extension to *.pot*).

Once the translations done, reupload the *.po* file to the development server and compile it to *.mo* file:
```bash
django-admin compilemessages
```
