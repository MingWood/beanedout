from datetime import datetime
import pycron

SCHEDULE = "* * * * * */8"

class PyCronExecutor(object):
    cron_func = None
    def __init__(self, cron_func):
        PyCronExecutor.cron_func = cron_func

    @pycron.cron(SCHEDULE)
    async def crontask(timestamp: datetime):
        print(f"Cron job running at {timestamp}")
        PyCronExecutor.cron_func()
        print(f"Cron complete")

    def start_cron(self):
        pycron.start()

if __name__ == '__main__':
    def example_func():
        print('im a test')
    test = PyCronExecutor(example_func)
    test.start_cron()
    