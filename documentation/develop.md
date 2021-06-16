# Development guide
## Build a distribution tarball
To build a specific distribution tarball:
```bash
git checkout v3.0
python setup.py sdist
```

The distribution will be located in **dist/** directory.


## Translation
To update the translation files, you need to deploy your code on a development server.

First, you can generate the language file:
```bash
cd /usr/local/lib/python3.6/site-packages/gerenuk_dashboard/
django-admin makemessages -l fr 
```

Next, download the *.po* file generated in **locale/fr/LC_MESSAGES/django.po**.
This file contains all the sentences to translate.

You can translate it manually or using a tool like [Zanata](https://translate.zanata.org/) (after changing the extension to *.pot*).

Once the translations done, reupload the *.po* file to the development server and compile it to *.mo* file:
```bash
django-admin compilemessages
```
