import time
import datetime
from main import LOGGER

from startup import LOG_PATH

today = datetime.datetime.today().strftime('%m%d%Y_%H%M')


def profile(func):
    """Write to log the profiling of a function."""
    # SortKey class is not present on the linux version
    # need to upgrade python to 3.7.4
    try:
        import io
        import pstats
        import cProfile
        from pstats import SortKey

        def inner(*args, **kwargs):
            pr = cProfile.Profile()
            pr.enable()
            value = func(*args, **kwargs)
            pr.disable()
            s = io.StringIO()
            sortby = SortKey.CUMULATIVE
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            ps.print_stats()
            with open(f'{LOG_PATH}/profile.log', 'w') as file:
                file.write(s.getvalue())
            return value
        return inner
    except ModuleNotFoundError:
        return lambda: ()


def total_time(func):
    """Write to log total time of function completition."""
    def wrapper(*args, **kwarg):
        start = time.time()
        value = func(*args, **kwarg)
        end = time.time()
        total = datetime.timedelta(seconds=end - start)
        caller = f"{args[0].__class__.__name__}.{func.__name__}"
        result = f"{caller} - total time: {str(total)}"
        LOGGER.info(result)
        with open(f'{LOG_PATH}/profile.log', 'a') as file:
            file.write(f'{today} - {result}')
        return value
    return wrapper
