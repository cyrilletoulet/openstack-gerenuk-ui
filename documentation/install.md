# OpenStack Gerenuk UI installation

## 1. Compatibility

| OpenStack release | OpenStack Gerenuk UI release | Gerenuk release |
| --- | --- | --- |
| Ussuri | 2.1 | 2.0.x |
| Train | 2.0 | 1.4.x |
| Stein | 2.0 | 1.4.x |



## 2. Prerequisites
### 2.1. Minimal deployment
First of all, you need to install [gerenuk](https://github.com/cyrilletoulet/gerenuk) API. 
Please refer to the Gerenuk documentation for details.

After installation, you should modify permissions of gerenuk config file to allow HTTPd server to read it:
```bash
chown apache:root /etc/gerenuk/gerenuk.conf
chmod 470 /etc/gerenuk/gerenuk.conf
```

### 2.2. Database configuration
Next, configure database in **/etc/gerenuk/gerenuk.conf** (see gerenuk config reference for details):
```
[database]
db_host = DB_HOST
db_name = gerenuk
db_user = gerenuk
db_pass = *secret*
```

*Don't forget to allow port 3306 from the dashobard to the cloud controller in firewall!*

### 2.3. Horizon configuration
Now, add the following lines to horizon settings (**/etc/openstack-dashboard/local_settings**):
```
# Gerenuk dashboard configuration
GERENUK_CONF = "/etc/gerenuk/gerenuk.conf"
PROJECT_MANAGER_ROLE = "project_manager"
```

### 2.4. OpenStack policies

Next, configure the OpenStack API policies to add the project manager role:
```
# In /etc/keystone/policy.yaml
"project_manager": "role:project_manager"
"identity:get_user": "(rule:project_manager) or (role:reader and system_scope:all) or (role:reader and token.domain.id:%(target.user.domain_id)s) or user_id:%(target.user.id)s"
```

Finally, restart the concerned APIs:
```bash
systemctl restart httpd.service
```


## 3. Install dashboard extension
### 3.1. Gerenuk OpenStack UI
Install the openstack-gerenuk-ui by copying python package:
```bash
pip3 install gerenuk_dashboard-2.1.tar.gz
cp /usr/local/lib/python3.6/site-packages/gerenuk_dashboard/enabled/* /usr/share/openstack-dashboard/openstack_dashboard/local/enabled/
```

And finally restart the HTTP server:
```bash
systemctl restart httpd
```

You should now find the new dashboard in **Project** / **Information** panel.
