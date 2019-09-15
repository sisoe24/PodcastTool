"""."""
import pathlib
import logging
import concurrent.futures

from podcasttool import gui_launch
from podcasttool import PodcastFile, generate_html, upload_to_server

LOGGER = logging.getLogger('podcast_tool.main')


def run_cli(path, test_env=False):
    """Run PodcastTool from command line.

    Arguments:
        path {str} - path where to parse for podcast files.
        test_env {bool} - if True then uploads to test folder in server {default: False}.
    """
    path = pathlib.Path(path).iterdir()
    for file in sorted(path):
        if file.name.endswith('.wav'):

            podcast = PodcastFile(file)
            podcast.generate_podcast()

    for file in podcast.files_to_upload():
        upload_to_server(file["path"], file["server_path"], test_env)

    generate_html(podcast.html_page)


def multi_threading(path, test_env=False):
    """Run PodcastTool from command line in multi threading.

    Arguments:
        path {str} - path where to parse for podcast files.
        test_env {bool} - if True then uploads to test folder in server {default: False}.
    """
    path = pathlib.Path(path).glob("*.wav")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for file in sorted(path):
            f1 = executor.submit(PodcastFile, file)
            podcast = f1.result()
            executor.submit(podcast.generate_podcast)

    generate_html(podcast.html_page)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for file in podcast.files_to_upload():
            executor.submit(upload_to_server,
                            file["path"], file["server_path"], test_env)


if __name__ == '__main__':
    # run_cli(path_long)
    # multi_threading(path_short)
    gui_launch.run()
