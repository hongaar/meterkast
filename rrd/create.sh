#!/bin/bash

rm electricity.rrd
# steps of 5 min
rrdtool create electricity.rrd --start N --step 300 \
DS:cons_counter:GAUGE:1800:1:U \
DS:cons_trend:DERIVE:1800:0:U \
DS:prod_counter:GAUGE:1800:1:U \
DS:prod_trend:GAUGE:1800:1:U \
RRA:AVERAGE:0.5:1:12 \
RRA:AVERAGE:0.5:1:288 \
RRA:AVERAGE:0.5:12:168 \
RRA:AVERAGE:0.5:12:744 \
RRA:AVERAGE:0.5:288:366

rm gas.rrd
# steps of 30 min
rrdtool create gas.rrd --start N --step 1800 \
DS:gas_counter:GAUGE:7200:1:U \
DS:gas_trend:DERIVE:7200:0:U \
RRA:AVERAGE:0.5:1:48 \
RRA:AVERAGE:0.5:1:336 \
RRA:AVERAGE:0.5:48:31 \
RRA:AVERAGE:0.5:48:366