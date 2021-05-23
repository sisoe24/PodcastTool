import os
import re
import sys
import ftplib
import logging

from tkinter import messagebox

import util

LOGGER = logging.getLogger('podcasttool.server')


class FtpServer:
    def __init__(self, server_path):
        self._server_path = server_path
        self.settings = util.UserConfig()

    def __enter__(self):
        try:
            self._ftp = ftplib.FTP(host=self.settings.value('host', 'x'),
                                   user=self.settings.value('user', 'x'),
                                   passwd=self.settings.value('pass', 'x'))
        except Exception as error:
            LOGGER.critical('Problem connecting %s', exc_info=True)
            util.open_log('Credentials probably wrong.')

        # self._ftp.login()

        return self._ftp

    def __exit__(self,  exc_type, exc_val, exc_tb):
        LOGGER.debug('Closing Ftp')
        self._ftp.close()


def check_server_path(server_path: str, test_env=False):
    """Check if path on server exists otherwise ask user to create new.

    Arguments:

        server_path (str) path on the server to check
        test_env (bool)   if True, upload to test path
    """
    test_server_path = util.UserConfig().data['test_url']

    server_path = server_path if not test_env else test_server_path

    # when checking path with ftp, https will cause error so it has be deleted
    server_path = server_path.replace("https://", "")

    LOGGER.debug("server path: %s", server_path)

    with FtpServer(server_path) as ftp:

        try:
            ftp.cwd(server_path)
        except ftplib.error_perm as ftp_error:
            LOGGER.critical("error ftp connessione: %s", ftp_error)

            user_prompt = messagebox.askyesno(
                title='PodcastTool',
                message=(f'Cartella {os.path.basename(server_path)}'
                         'non esiste sul server.\nVuoi crearla?'))
            if user_prompt:
                LOGGER.debug('creating directory: %s', server_path)
                ftp.mkd(server_path)
            else:
                messagebox.showerror(title='PodcastTool',
                                     message=('Impossibile procedere.'
                                              '\nCreare la cartella'
                                              '\nmanualmente e riprovare'))
                sys.exit('Exit App')
        except Exception as error:
            LOGGER.critical('exception when cwd to ftp', exc_info=True)
            util.open_log('Unexpected error uploading to server.')

    return server_path


def upload_to_server(uploading_file: str, server_path: str, test_env=False):
    """Upload podcast file to server.

    Arguments:

        str uploading_file path of the file to upload
        str server_path    path on the server where to upload the file
    """

    with FtpServer(server_path) as ftp:

        ftp.cwd(server_path)

        with open(uploading_file, 'rb') as upload:
            LOGGER.debug('uploading file on server: %s', uploading_file)

            # if user is me then app will NOT upload to server
            if util.is_dev_mode(bypass=test_env):
                LOGGER.info('FAKE UPLOAD: %s in %s', uploading_file, ftp.pwd())
                return

            file_name = os.path.basename(uploading_file)
            status = ftp.storbinary(f'STOR {file_name}', upload)

            status = re.sub(r'226-?|\(measured\shere\)|\n', '', str(status))

            LOGGER.info(status)
            LOGGER.debug('status: %s', status)
            LOGGER.debug('uploaded file to server: %s', file_name)
