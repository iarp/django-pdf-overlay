import io
from setuptools import setup

long_description = io.open('README.rst', encoding='utf-8').read()

# Dynamically calculate the version based on allauth.VERSION.
version = __import__('django_pdf_filler').__version__

METADATA = dict(
    name='django-pdf-filler',
    version=version,
    author='IARP',
    author_email='iarp.comptech@gmail.com',
    description='Supply and fill PDFs',
    long_description=long_description,
    url='http://github.com/iarp/django-pdf-filler',
    keywords='django pdf overlay',
    tests_require=[],
    install_requires=['Django >= 1.11', 'django-bootstrap4 >= 0.0.8', 'PyPDF2 >= 1.26.0', 'reportlab >= 3.5.23'],
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
    packages=['django_pdf_filler'],
)

if __name__ == '__main__':
    setup(**METADATA)
