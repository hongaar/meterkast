import rrdtool
import tempfile

class Writer:

    ranges = [
        {'range': 'hour', 'title': 'afgelopen uur'},
        {'range': 'day', 'title': 'afgelopen dag'},
        {'range': 'week', 'title': 'afgelopen week'},
        {'range': 'month', 'title': 'afgelopen maand'},
        {'range': 'year', 'title': 'afgelopen jaar'}
    ]

    def __init__(self, data):
        self.electricity_db = '/home/pi/code/rrd/electricity.rrd'
        self.gas_db = '/home/pi/code/rrd/gas.rrd'
        self.www = '/home/pi/code/www/'
        self.data = data

    def write(self, cnt_consumption, cnt_production, cnt_gas):
        # Counters are in kWh, convert to Wh
        cnt_consumption = int(cnt_consumption * 1000)
        cnt_production = int(cnt_production * 1000)

        # Counter is in m3, convert to dm3
        cnt_gas = int(cnt_gas * 1000)

        # multiply by 1000 to get mWh for DERIVE data-sets
        if cnt_consumption > 0:
            update_str = 'N:%i:%i:%i:%i' % (cnt_consumption, cnt_consumption * 1000, cnt_production, cnt_production * 1000)
            rrdtool.update(self.electricity_db, update_str)
        self.update_electricity_graph()

        # multiply by 1000 to get cm3 for DERIVE data-sets
        if cnt_gas > 0:
            update_str = 'N:%i:%i' % (cnt_gas, cnt_gas * 1000)
            rrdtool.update(self.gas_db, update_str)
        self.update_gas_graph()

    def update_electricity_graph(self):
        for i, val in enumerate(self.ranges):
            path = self.www + 'electricity-' + str(i) + '-' + val['range'] + '.png'

            # To go from mWh/s to W, multiply by 3.6

            # To go from mWh to kWh, divide by 1000000

            result = rrdtool.graph(path,
                '--imgformat', 'PNG',
                '--width', '1024',
                '--height', '320',
                '--start', "-1%s" % val['range'],
                '--end', "now",
                '--vertical-label', 'Watt',
                '--title', 'Electriciteit (%s)' % val['title'],
                '--lower-limit', '0',
                'DEF:cons_trend=%s:cons_trend:AVERAGE' % self.electricity_db,
                'CDEF:corr_cons=cons_trend,3.6,*',
                'DEF:prod_trend=%s:prod_trend:AVERAGE' % self.electricity_db,
                'CDEF:corr_prod=prod_trend,3.6,*',
                'LINE1:corr_cons#ff0000:Afname',
                'LINE1:corr_prod#00ff00:Levering',
                'CDEF:corr_total=cons_trend,1000000,/',
                'VDEF:cons_total=corr_total,TOTAL',
                'GPRINT:cons_total:Total\: %6.2lf kWh',
                'PRINT:cons_total:%6.2lf')

            self.data.set('cons_avg_' + val['range'], float(result[2][0]))

    def update_gas_graph(self):
        for i, val in enumerate(self.ranges):
            path = self.www + 'gas-' + str(i) + '-' + val['range'] + '.png'

            # To go from cm3 to m3, divide by 1000000

            result = rrdtool.graph(path,
                '--imgformat', 'PNG',
                '--width', '1024',
                '--height', '320',
                '--start', "-1%s" % val['range'],
                '--end', "now",
                '--vertical-label', 'm3',
                '--title', 'Gas (%s)' % val['title'],
                '--lower-limit', '0',
                'DEF:gas_trend=%s:gas_trend:AVERAGE' % self.gas_db,
                'CDEF:corr_gas=gas_trend,0.0036,*',
                'LINE1:corr_gas#ff0000:Afname',
                'CDEF:corr_total=gas_trend,1000000,/',
                'VDEF:gas_total=corr_total,TOTAL',
                'GPRINT:gas_total:Total\: %6.2lf m3',
                'PRINT:gas_total:%6.2lf')

            self.data.set('gas_avg_' + val['range'], float(result[2][0]))
