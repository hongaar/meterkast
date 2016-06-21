import rrdtool
import tempfile

class Writer:

    def __init__(self):
        self.electricity_db = 'rrd/electricity.rrd'
        self.gas_db = 'rrd/gas.rrd'
        self.www = 'www/'

    def write(self, cnt_consumption, cnt_production, cnt_gas):
        # Counters are in kWh, convert to Wh
        cnt_consumption = int(cnt_consumption * 1000)
        cnt_production = int(cnt_production * 1000)

        # Counter is in m3, convert to dm3
        cnt_gas = int(cnt_gas * 1000)

        # multiply by 1000 to get mWh for DERIVE data-sets
        update_str = 'N:%i:%i:%i:%i' % (cnt_consumption, cnt_consumption * 1000, cnt_production, cnt_production * 1000)
        rrdtool.update(self.electricity_db, update_str)
        self.update_electricity_graph()

        # multiply by 1000 to get cm3 for DERIVE data-sets
        update_str = 'N:%i:%i' % (cnt_gas, cnt_gas * 1000)
        rrdtool.update(self.gas_db, update_str)
        self.update_gas_graph()


    def update_electricity_graph(self):
        ranges = {
            'afgelopen minuut': '-1minute',
            'afgelopen uur': '-1hour',
            'afgelopen dag': '-1day',
            'afgelopen week': '-1week',
            'afgelopen maand': '-1month',
            'afgelopen jaar': '-1year'
        }

        for key, value in ranges.iteritems():
            path = self.www + 'electricity' + value + '.png'

            # To go from mWh/s to W, multiply by 3.6

            rrdtool.graph(path,
              '--imgformat', 'PNG',
              '--width', '1024',
              '--height', '320',
              '--start', "%s" % value,
              '--end', "now",
              '--vertical-label', 'Watt',
              '--title', 'Electriciteit (%s)' % key,
              '--lower-limit', '0',
              'DEF:cons_trend=%s:cons_trend:AVERAGE' % self.electricity_db,
              'CDEF:corr_cons=cons_trend,3.6,*',
              'DEF:prod_trend=%s:prod_trend:AVERAGE' % self.electricity_db,
              'CDEF:corr_prod=prod_trend,3.6,*',
              'LINE1:corr_cons#ff0000:Afname',
              'LINE1:corr_prod#00ff00:Levering')

    def update_gas_graph(self):
        ranges = {
            'afgelopen uur': '-1hour',
            'afgelopen dag': '-1day',
            'afgelopen week': '-1week',
            'afgelopen maand': '-1month',
            'afgelopen jaar': '-1year'
        }

        for key, value in ranges.iteritems():
            path = self.www + 'gas' + value + '.png'

            # To go from cm3/s to m3, multiply by 0.0036

            rrdtool.graph(path,
              '--imgformat', 'PNG',
              '--width', '1024',
              '--height', '320',
              '--start', "%s" % value,
              '--end', "now",
              '--vertical-label', 'm3',
              '--title', 'Gas (%s)' % key,
              '--lower-limit', '0',
              'DEF:gas_trend=%s:gas_trend:AVERAGE' % self.gas_db,
              'CDEF:corr_gas=gas_trend,0.0036,*',
              'LINE1:corr_gas#ff0000:Afname')
