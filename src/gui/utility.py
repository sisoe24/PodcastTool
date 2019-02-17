"""Reusable utility functions."""
import os
import json
import time
import pathlib
import logging
import datetime


logger = logging.getLogger('podcast_tool.utlity')


def profile(func):
    """Write to log the profiling of a function."""
    # XXX SortKey not working on linux
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
        with open(f'{get_path("log")}/profile.log', 'a') as f:
            f.write(s.getvalue())
        return value
    return inner


def total_time(func):
    """Write to log total time of function completition."""
    def wrapper(*args, **kwarg):
        start = time.time()
        value = func(*args, **kwarg)
        end = time.time()
        total = datetime.timedelta(seconds=end - start)
        print_str = f"total time: {str(total)}\n"
        print(print_str)
        with open(f'{get_path("log")}/profile.log', 'a') as f:
            f.write(print_str)
    return wrapper


def get_path(directory: str) -> str:
    """Search for the path in main working directory.

    Get path of the argument string directory if is in root PodcastTool folder.
    """
    file_path = pathlib.Path(os.path.dirname(__file__))
    for path in file_path.parents:
        if path.parts[-1] == 'PodcastTool2':
            new_path = path.joinpath(directory)
            break
    return new_path if os.path.exists(new_path) else exit("no path found")


def catalog_names() -> str:
    """Open json catalog of names to grab the teachers and courses names."""
    # json file should always be in
    # the same directory of where the src code is
    json_file = os.path.join(
        os.path.dirname(__file__), 'catalog_names.json')
    try:
        with open(json_file) as f:
            logger.debug(f'parsing json file: {json_file}')
            json_data = json.load(f)
            return json_data
    except FileNotFoundError:
        print('no json file found!', json_file)
        logger.warning(f'No json file found: {json_file}')
        exit()


if __name__ == '__main__':
    pass
    # get_path('log')
