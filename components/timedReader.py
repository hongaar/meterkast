from helpers.timer import TaskThread


class TimedReader(TaskThread):
    DEFAULT_INTERVAL = 1 * 60
    HIBERNATION_INTERVAL = 5 * 60
    DEBUG_INTERVAL = 5

    probing_callback = None
    probed_callback = None

    def __init__(self, p1, debug=False):
        TaskThread.__init__(self)

        self.debug = debug
        self.p1 = p1
        self.set_interval(self.DEFAULT_INTERVAL)

    def set_interval(self, interval):
        if self.debug:
            TaskThread.set_interval(self, self.DEBUG_INTERVAL)
        else:
            TaskThread.set_interval(self, interval)

    def wakeup(self):
        self.set_interval(self.DEFAULT_INTERVAL)

    def hibernate(self):
        self.set_interval(self.HIBERNATION_INTERVAL)

    def event_probing_setup(self, callback):
        self.probing_callback = callback

    def event_probed_setup(self, callback):
        self.probed_callback = callback

    def event_start(self):
        self.start()

    def event_stop(self):
        self.shutdown()

    def task(self):
        self.probing_callback()
        data = self.p1.probe()
        self.probed_callback(data)
