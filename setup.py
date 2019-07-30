import io
from setuptools import find_packages, setup

long_description = io.open('README.rst', encoding='utf-8').read()

# Dynamically calculate the version based on allauth.VERSION.
version = __import__('django_pdf_overlay').__version__

METADATA = dict(
    name='django-pdf-overlay',
    version=version,
    author='IARP',
    author_email='iarp.opensource@gmail.com',
    description='Fill PDFs from model instances',
    long_description=long_description,
    url='http://github.com/iarp/django-pdf-overlay',
    keywords='django pdf overlay',
    tests_require=[],
    install_requires=['Django >= 1.11', 'django-bootstrap4', 'PyPDF2', 'reportlab'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
        'Topic :: Internet',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
    ],
    packages=find_packages(),
    project_urls={
        'Documentation': 'https://django-pdf-overlay.readthedocs.io/en/latest/',
        'Source': 'https://github.com/iarp/django-pdf-overlay/',
        'Tracker': 'https://github.com/iarp/django-pdf-overlay/issues',
    },
)

if __name__ == '__main__':
    setup(**METADATA)
