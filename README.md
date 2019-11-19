# The OpenStack Gerenuk UI

This UI is a dashboard extension for Horizon project.


## Manual installation

```bash
cp -r gerenuk_dashboard /usr/lib/python2.7/site-packages/
cp /usr/lib/python2.7/site-packages/gerenuk_dashboard/enabled/* /usr/share/openstack-dashboard/openstack_dashboard/local/enabled/
```

## Development
### Translation

To update the translation files, you need to deploy your code on a development server.

If you generate a language file for the first time, you need to create the locale dir first. 
For example, the french locale:
```bash
cd /usr/lib/python2.7/site-packages/gerenuk_dashboard/
mkdir -p locale/fr/LC_MESSAGES/
```

Next, you can generate the language file:
```bash
django-admin makemessages -l fr 
```

Next, download the *.po* file generated in **locale/fr/LC_MESSAGES/django.po**.
This file contains all the sentences to translate.

You can translate it manually or using a tool like [Zanata](https://translate.zanata.org/) (after changing the extension to *.pot*).

Once the translations done, reupload the *.po* file to the development server and compile it to *.mo* file:
```bash
django-admin compilemessages
```
