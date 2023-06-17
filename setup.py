from setuptools import setup

setup(
    name='whatsapp',
    version='1.0',
    description='Controll whatsapp web',
    packages=['whatsapp'],
    package_data={'whatsapp': ['xpath.json']},
    install_requires=[
        'selenium',
        'webdriver_manager',
        'qrcode',
        'Pillow'
    ]
)
