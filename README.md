# Meterkast 

## Matrix display

### Part & wiring

MAX7219
[Buy](https://www.bitsandparts.eu/LED_Matrix_Display_Module_8x8_MAX7219_(Displays_and_EL_wire)-p100697.html)

### Software

[GitHub](https://github.com/rm-hull/max7219)

```
$ cd max7219
$ sudo apt-get install python-dev python-pip
$ sudo pip install spidev
$ sudo python setup.py install
```

## Movement sensor

### Part & Wiring

HC-SR501
[Buy](http://www.bitsandparts.eu/Bewegingssensor-bewegingsmelder_Infrarood-IR_PIR_-_HC-SR501_(Bewegingssensors)-p109693.html)
[Specs](https://www.mpja.com/download/31227sc.pdf)

### Software

None, analog sensor

## RGB led

### Part & Wiring

WS2812
[Buy](https://www.conrad.nl/nl/linker-kit-led-printplaat-lk-led-rgb-meerkleurig-1371347.html)
[Specs](http://www.produktinfo.conrad.com/datenblaetter/1300000-1399999/001371347-an-01-de-LINKER_KIT_RGB_LED_MEHRFARBIG.pdf)

Connect to pin 13 / channel 1 on 3.3v rail.

### Software

[GitHub](https://github.com/jgarff/rpi_ws281x)

```
$ sudo apt-get install scons
$ cd rpi_ws281x
$ sudo scons
$ cd python
$ sudo python setup.py install
```

## OLED display

SSD1306
Buy
[Specs](http://linkerkit.de/lib/exe/fetch.php?media=001318257-an-01-de-oled_display_0_96_zoll_fuer_raspberry.pdf)

### Software

[GitHub](https://github.com/adafruit/Adafruit_Python_SSD1306)

```
$ sudo apt-get install python-imaging python-smbus
```

## P1

[Tutorial](http://gejanssen.com/howto/Slimme-meter-uitlezen/)

```
$ sudo apt-get install cu minicom
```

## Joystick

### Part & Wiring

[Specs](http://linksprite.com/wiki/index.php5?title=Joystick_Sensor_Module)

Use wiring from https://learn.adafruit.com/reading-a-analog-in-and-controlling-audio-volume-with-the-raspberry-pi/script and http://ww1.microchip.com/downloads/en/DeviceDoc/21295C.pdf

### Software

None, analog sensor