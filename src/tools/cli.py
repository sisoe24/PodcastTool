import concurrent.futures
import os
import pathlib

from . import PodcastFile, check_server_path, generate_html, upload_to_server


def run_single_thread(path, test_env=False):
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


def run_multi_thread(path, test_env=False):
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


def _test_podcast():
    """Testing the PodcastFile. No use in production."""
    path = pathlib.Path(os.environ['TEST_DIR']).joinpath('ALP/MULO')
    for file in path.glob("*wav"):
        podcast = PodcastFile(file)
        podcast.generate_podcast()
    files = list(podcast.files_to_upload())[0]["server_path"]
    print(files)


def _test_cli():
    file = os.path.dirname(os.path.dirname(__file__))
    _path = os.path.join(file, 'other/Scrivania/ALP/ALP1')
    run_single_thread(_path, test_env=True)
    run_multi_thread(_path, test_env=True)


if __name__ == '__main__':
    pass
