# The OpenStack Gerenuk UI

This UI is a dashboard extension for Horizon project.


## Manual installation

```bash
cp -r gerenuk_dashboard /usr/lib/python2.7/site-packages/
cp /usr/lib/python2.7/site-packages/gerenuk_dashboard/enabled/* /usr/share/openstack-dashboard/openstack_dashboard/local/enabled/
```

## Trasnlation
The first step is to create a PO file for the new language and then compile it ( during each modification to this file, it is necessary to recompile it )
```bash
cd /usr/lib/python2.7/site-packages/gerenuk_dashboard/
django-admin makemessages -l fr 
django-admin compilemessages
```

