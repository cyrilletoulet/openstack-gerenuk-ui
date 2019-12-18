# The OpenStack Gerenuk UI

This UI is a dashboard extension for Horizon project.

## Build distribution tarball

To build a distribution tarball:
```bash
python setup.py sdist
```

The distribution will be located in **dist/** directory.


## Installation

First of all, you need to install [gerenuk](https://github.com/cyrilletoulet/gerenuk) API:
```bash
yum-config-manager --enable epel
yum -y install python-pip mysql-connector-python
yum-config-manager --disable epel
pip install gerenuk-1.3.0.tar.gz
mkdir /etc/gerenuk
chmod 711 /etc/gerenuk
touch /etc/gerenuk/gerenuk.conf
chmod -R 644 /etc/gerenuk/gerenuk.conf
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

Install the openstack-gerenuk-ui by copying python package:
```bash
pip install gerenuk_dashboard-0.7.tar.gz
cp /usr/lib/python2.7/site-packages/gerenuk_dashboard/enabled/* /usr/share/openstack-dashboard/openstack_dashboard/local/enabled/
```

And finally restart the HTTP server:
```bash
systemctl restart httpd
```

You should now find the new dashboard in **Project** / **Information** panel.


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
