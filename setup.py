from setuptools import find_packages, setup

setup(
    name = "gerenuk_dashboard",
    version = "2.1",
    description = "The Gerenuk dashboard for OpenStack",
    url = "https://github.com/cyrilletoulet/openstack-gerenuk-ui",

    license = "GPL",
    classifiers = [
        "License :: OSI Approved :: GPL v3 license",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],

    keywords = "monitoring cloud openstack gerenuk",

    author = "Cyrille TOULET, Iheb ELADIB",
    author_email = "hpc@univ-lille.fr",

    package_data = {"": ["README", "*.html", "*.po", "*.mo"],
                    "gerenukd_dashboard.enabled": ["*"]},
    include_package_data=True,
    packages = find_packages(include=["gerenuk_dashboard", "gerenuk_dashboard.*"]),

    python_requires = ">=3.0",
)
