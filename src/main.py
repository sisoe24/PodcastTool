"""."""
import pathlib

from podcasttool import PodcastFile, generate_html, upload_to_server
from podcasttool import logger
from podcasttool import util
from podcasttool import gui_launch


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


if __name__ == '__main__':
    gui_launch.run()
