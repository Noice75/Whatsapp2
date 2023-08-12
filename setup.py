from setuptools import setup

setup(
    name='whatsapp',
    version='1.0',
    description='Control WhatsApp Web',
    packages=['whatsapp'],
    package_data={'whatsapp': ['xpath.json', 'commands/*']},
    install_requires=[
        'selenium',
        'webdriver_manager',
        'qrcode',
        'Pillow',
        'beautifulsoup4'
    ],
    entry_points={
        'console_scripts': [
            'whatsapp-control = whatsapp.main:main',
        ],
    },
)
