"""Setup script for seobot package."""
from setuptools import setup, find_packages

setup(
    name="seobot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'google-api-python-client==2.108.0',
        'google-auth-httplib2==0.1.1',
        'google-auth-oauthlib==1.1.0',
        'pandas==2.1.3',
        'pyyaml==6.0.1',
        'python-dotenv==1.0.0',
    ],
)
