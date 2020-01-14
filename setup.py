from setuptools import find_packages, setup

setup(
    name = "gerenuk_dashboard",
    version = "1.1",
    description = "The Gerenuk dashboard for OpenStack",
    url = "https://github.com/cyrilletoulet/openstack-gerenuk-ui",

    license = "GPL",
    classifiers = [
        "License :: OSI Approved :: GPL v3 license",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ],

    keywords = "monitoring cloud openstack gerenuk",

    author = "Iheb ELADIB",
    author_email = "iheb.eladib@univ-lille.fr",

    package_data = {"": ["README", "*.html", "*.po", "*.mo"],
                    "gerenukd_dashboard.enabled": ["*"]},
    include_package_data=True,
    packages = find_packages(include=["gerenuk_dashboard", "gerenuk_dashboard.*"]),

    python_requires = ">=2.7,!=3.*",
)
