#!/bin/sh

sudo service meterkast stop
sudo update-rc.d -f meterkast remove
sudo rm /etc/init.d/meterkast
sudo cp meterkast /etc/init.d/meterkast
sudo chmod a+x /etc/init.d/meterkast
sudo update-rc.d meterkast defaults
/etc/init.d/meterkast start