from setuptools import setup, find_packages


setup(
    name = "django-waitinglist",
    version = "1.0b11",
    author = "Brian Rosner",
    author_email = "brosner@gmail.com",
    description = "a Django waiting list app for running a private beta with cohorts support",
    long_description = open("README.rst").read(),
    license = "MIT",
    url = "http://github.com/pinax/django-waitinglist",
    packages = find_packages(),
    package_data = {"waitinglist": ["templates/*/*"]},
    install_requires = [
        "django-appconf==0.5",
    ],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)