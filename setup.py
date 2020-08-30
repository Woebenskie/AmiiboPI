from setuptools import setup

setup(
    name='AmiiboPI',
    version='0.1',
    packages=['joycontrol'],
    url='https://github.com/Woebenskie/AmiiboP',
    license='GPL-3.0',
    author='Ruben',
    author_email='',
    description='To send Amiibo to Nintendo switch via a Raspberry PI with display and buttons.'
    install_requires=[
        'hid', 'aioconsole', 'dbus-python', 'crc8'
]
)
