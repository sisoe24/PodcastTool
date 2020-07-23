"""."""
import os
import pathlib
import logging
import concurrent.futures

from podcasttool import gui_launch
from podcasttool import (
    PodcastFile,
    generate_html,
    upload_to_server,
    check_server_path
)

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
        server_path = check_server_path(file["server_path"], test_env)
        upload_to_server(file["path"], server_path)

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

    check_path = list(podcast.files_to_upload())[0]["server_path"]
    server_path = check_server_path(check_path, test_env)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for file in podcast.files_to_upload():
            executor.submit(upload_to_server, file["path"], server_path)

    generate_html(podcast.html_page)


def class_test():
    """Testing the PodcastFile. No use in production."""
    path = pathlib.Path(os.environ['TEST_DIR']).joinpath('ALP/MULO')
    for file in path.glob("*wav"):
        podcast = PodcastFile(file)
        podcast.generate_podcast()
    files = list(podcast.files_to_upload())[0]["server_path"]
    # print(files[0]["server_path"])
    print(files)


if __name__ == '__main__':
    # class_test()
    # run_cli()
    # multi_threading(os.environ["TEST_DIR"])
    gui_launch.run()
