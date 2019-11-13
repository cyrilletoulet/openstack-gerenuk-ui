# The OpenStack Gerenuk UI

This UI is a dashboard extension for Horizon project.


## Manual installation

First of all, you need to install [gerenuk](https://gitlab-dsi.univ-lille.fr/hpc/gerenuk) API:
```bash
yum-config-manager --enable epel
yum -y install python-pip mysql-connector-python
yum-config-manager --disable epel
pip install gerenuk-1.2.4.tar.gz
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
cp -r gerenuk_dashboard /usr/lib/python2.7/site-packages/
cp /usr/lib/python2.7/site-packages/gerenuk_dashboard/enabled/* /usr/share/openstack-dashboard/openstack_dashboard/local/enabled/
```

And finally restart the HTTP server:
```bash
systemctl restart httpd
```

You should now find the new dashboard in **Project** / **Information** panel.
