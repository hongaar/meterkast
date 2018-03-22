#!/bin/sh

sudo rm /etc/logrotate.d/meterkast
sudo cp meterkast /etc/logrotate.d/meterkast
sudo chmod a+r /etc/logrotate.d/meterkast
