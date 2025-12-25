# pi-frame

A digital picture frame with a Raspberry Pi and e-ink screen.

![pi-frame](IMG_5798.jpg)


## Hardware

* Pi Zero 2 W (https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/) + power suppply and micro SD card
* Inky Imperssion e-ink screen (https://shop.pimoroni.com/products/inky-impression-7-3?variant=55186435277179)
* 4 x square nut 2-56 thread (https://www.mcmaster.com/catalog/131/3657/94855A279)
* 4 x flat head screw 2-56 thread 3/8" (https://www.mcmaster.com/catalog/131/3494/96640A025)
* 2 x pan head screw M2.5 8mm (https://www.mcmaster.com/catalog/131/3456/95836A255)
* 1 x 1/8"x12" brass rod (optional)

3D prints:
* Standing frame (Frame 1 Print.stl) or wall frame (Frame 2 Print.stl)
* Spacers (Spacers Print.stl)

No printing supports are necessary, using a brim can help adhesion for
the spacers.

Attach the Pi header pins to the back of the display, following the outline
printed on the disply for orientation. Use the spacers and M2.5 screws to
secure the Pi to the standoffs.

Attach the two halfs of the frame with the 2-56 screws and nuts. A brass rod
can be added to the frame to improve stability.

Standing frame:
![Standing Frame]("Frame 1 Render.png")

Wall frame:
![Wall Frame]("Frame 2 Render.png")


## Raspberry Pi Setup

Install Raspberry Pi OS.

Configure with `raspi-config`:
* Enable wifi, ssh, and i2c
* Set the timezone

Install software:
```
$ sudo apt-get update
$ sudo apt-get install python3-dev libjpeg-dev libpng-dev libfreetype-dev libharfbuzz-dev git
```


## E-Ink Setup

Clone the repository and install software:
```
$ cd $HOME
$ git clone https://github.com/pimoroni/inky
$ cd inky
$ ./install.sh
```


## pi-frame Setup

Clone the repo:
```
$ cd $HOME
$ git clone https://github.com/darbyjohnston/pi-frame.git
$ cd pi-frame
```

Download the image collection:
```
$ python download.py
```

Display a random image from the collection:
```
$ ./run.sh
```

Add a cron job:
```
$ crontab -e:
@reboot /home/pi/pi-frame/run.sh > /home/pi/pi-frame/log.txt 2>&1
0 7-21 * * * /home/pi/pi-frame/run.sh > /home/pi/pi-frame/log.txt 2>&1
```

