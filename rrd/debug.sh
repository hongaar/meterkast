#!/bin/bash

rm power.rrd
rrdtool create power.rrd --start N --step 5 \
DS:consumption:DERIVE:60:0:U \
DS:production:DERIVE:60:0:U \
DS:gas:DERIVE:60:0:U \
RRA:AVERAGE:0.5:1:12 \
RRA:AVERAGE:0.5:12:60