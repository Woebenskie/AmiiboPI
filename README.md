# AmiiboPI

To send Amiibo to Nintendo switch via a Raspberry PI with display and buttons.

Tested on RPI zeroW with raspberrypi os

Find Eagle and Fusion360 Files in this repo: [Extras](https://github.com/Woebenskie/AmiiboPI-extra)

## Looks

## Parts List
Raspberry pi ZeroW With Female GPIO

3 push buttons.

1 SSD1306 0.96 i2c oled screen.

1 custom pcb can be found in the other repo.

1 by 9 Pin headers (cut in 1 by 7 and 1 by 2)

--optional:

3D Printer #to create the enclosure find stl's in other repo.
## Installation

Package it self:

```bash
cd /opt/
git clone https://github.com/Woebenskie/AmiiboPI.git
```

Requirements:

```bash
cd /opt/AmiiboPI/
pip3 install .
pip3 install -r requirements.txt
apt install python3-dbus libhidapi-hidraw0
```

## Usage
Either run via sudo or as root user.

```bash
python3 main.py
```
Run as service:
```bash
nano /lib/systemd/system/amiibopi.service

[Unit]
Description=AmiiboPI

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/AmiiboPI/main.py

[Install]
WantedBy=multi-user.target

systemctl enable amiibopi.service
systemctl start amiibopi.service
```
## Credits
Credits to:
[mart1nro](https://github.com/mart1nro) for the joycontrol libary.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)
