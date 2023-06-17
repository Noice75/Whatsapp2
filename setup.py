from setuptools import setup

setup(
    name='whatsapp',
    version='1.0',
    description='Controll whatsapp web',
    packages=['whatsapp'],
    install_requires=[
        'selenium',
        'webdriver_manager',
        'qrcode',
        'Pillow'
    ],
    entry_points={
        'console_scripts': [
            'whatsapp = whatsapp.main:main'
        ]
    }
)
