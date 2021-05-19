"""Podcast generator for Fonderie Sonore.

Generates an audio file to upload to a server, from a podcast registration.
The audio file has audio cue at the beginning
of the stream for the name of the teacher, the name of the course, the date,
the lesson number, and the part number.

The name of the file is always formatted like this:
    SEC6_20133201_E_Cosimi_Lezione_4_Parte_1.wav.
"""
import os
import sys
import math
import wave
import ftplib
import shutil
import hashlib
import pathlib
import logging

from datetime import datetime
from tkinter import messagebox

import pydub
import regex
import yattag

from podcasttool import util

LOGGER = logging.getLogger('podcast_tool.generate_podcast')


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
            messagebox.showerror(title='PodcastTool',
                                 message='Credentials probably wrong')
            LOGGER.critical('Problem connecting %s', exc_info=True)
            sys.exit('Exit App')

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
                message=(f'Cartella {os.path.basename(server_path)} '
                         'non esiste sul server\nVuoi crearla?'))
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
            messagebox.showerror(
                'PodcastTool', message='Unexpected error when changing dir in ftp')
            LOGGER.critical('exception when cwd to ftp', exc_info=True)
            sys.exit()

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
            status_sub = regex.sub(
                r'226|-|\(measured here\)|\n', '', str(status))
            LOGGER.info(status_sub)
            LOGGER.debug('status: %s', status_sub)
            LOGGER.debug('uploaded file to server: %s', file_name)


class PodcastFile:
    """Construct method for the PodcastFile class.

        Arguments:

            raw_podcast {string} -- full path like string of the podcast file.
    """
    _html_page = {
        "archive_name": "",
        "registration_date": "",
        "course_name": "",
        "teacher_name": "",
        "lesson": "",
        "parts": {}
    }
    missing_audio = set()

    def __init__(self, raw_podcast: str):
        LOGGER.debug('Initialize PodcastFile class ->')

        self.__name, _ = os.path.splitext(os.path.basename(raw_podcast))
        self._check_valid_file(self.__name + ".wav")

        # podcast names have always this structure:
        # ex: SEC6_20133201_E_Cosimi_Lezione_4_Parte_1.wav
        self._splitted_name = self.__name.split('_')
        LOGGER.debug('podcast name splitted: %s', self._splitted_name)

        self.__abspath = raw_podcast
        LOGGER.debug('podcast file absolute path: %s', self.__abspath)

        self.__directory = os.path.dirname(raw_podcast)
        LOGGER.debug('podcast file directory: %s', self.__directory)

        self._course_path = None
        self._audio_intro = None

    def __iter__(self):
        """Return all elements of the podcast file.

        Return:
            [list] - all elements of podcast file.
        """
        all_data = [
            self.name,
            self.teacher_name,
            self.course_name,
            self.lesson_number,
            self.part_number,
            self.registration_date,
            self.directory
        ]
        return iter(all_data)

    def __len__(self):
        """Get the lenght of the audio in milliseconds.

        I made this because pydub on some occasions, when rouding the duration
        from float to int, left a microsecond out
        (e.g. part1=1m, part2=2m, part3=0000000.1s) and as a result,
        when splitting the podcast there was a part so short that it couldn't
        be opened by anything. Therefore I made this to prevent that for ever
        happening.

        But I have probably solved and should investigate further if I still
        need this function.

        Returns:
            {int} - return in ms of the lenght audio

        """
        try:
            with wave.open(self.__abspath, 'rb') as wave_file:
                nframe = wave_file.getnframes()
                rframe = wave_file.getframerate()
        except Exception as error:
            LOGGER.critical('%s - probably not a wave file!', error)
            # TODO: need to show the message to user
            sys.exit()

        # amount in seconds
        total_float_seconds = nframe / rframe
        total_ms = math.ceil(total_float_seconds * 1000)

        LOGGER.debug("total_ms %d", total_ms)
        LOGGER.debug("total_float_seconds %f", total_float_seconds)
        return total_ms

    @staticmethod
    def _check_valid_file(filename):
        """If calling this class by CLI then needs to check whetever the file
        has a valid podcast structure.
        """
        valid_file = regex.match(r'''
                    [A-Z]+(\d+)?_        # course name
                    \d{8}_               # registration date
                    [A-Z]_               # teacher initial letter
                    [A-Za-z]+_           # teacher surname
                    Lezione_\d{1,2}_     # lesson number
                    parte_\d{1,2}\.wav   # part number
                    ''', filename, regex.I | regex.X)
        if not valid_file:
            LOGGER.critical(
                "La nomenclatura del file sembra invalida %s", filename)
            # TODO: need to show the message to user
            sys.exit()

    @property
    def name(self):
        """Return string representation of the file name."""
        return str(self.__name)

    @property
    def abspath(self):
        """Return string representation of absolute path of the raw podcast."""
        return str(self.__abspath)

    @property
    def directory(self):
        """Return string representation of the directory of the file."""
        return str(self.__directory)

    @property
    def html_page(self) -> dict:
        """Get the podcast html information from class dictionary data.

        The html informations is needed for generating the podcast page.
        If need parts is better to call files_to_upload().
        Structure of the dict:
            "archive_name": "",
            "registration_date": "",
            "course_name": "",
            "teacher_name": "",
            "lesson": "",
            "parts": {"link":"", "duration":"", "path": "", "server_path":""}
        Return:
            [dict] - dictionary with html_elements
        """
        return self._html_page

    def files_to_upload(self) -> dict:
        """ Return a dict_values iterator with the podcast parts information.

        Values of dictionary:
            link = link on the server where the file is going to be uploaded.
            path = path of the file that is going to be uploaded.
            server_path = server path of the file that is going to be uploaded
            duration = duration of the podcast file.
        """
        return self.html_page["parts"].values()

    @property
    def course_name(self):
        """Get the full course name of the parsed file.

        Returns:
            [str] - - the full name of the course name.

        """
        code = self._splitted_name[0]
        LOGGER.debug('course code from file: %s', code)

        # the code is always the first 3 strings in the name
        course_code, edition = regex.sub(
            r'([A-Z]{3})([A-Z]{1,3}|\d{1,3})', r'\1 \2', code).split(' ')

        LOGGER.debug('codice corso, edizione: %s, %s', course_code, edition)

        courses_names = util.catalog_names("corsi")
        course_info = courses_names[course_code]
        self._course_path = f"{course_info['course_path']}/{code}"

        course = course_info['course_name']
        LOGGER.debug('get complete course name: %s', course)

        self.html_page['course_name'] = course

        return course

    @property
    def course_path(self):
        """Get the parent folder of the podcast course."""
        LOGGER.debug("course path: %s", self._course_path)
        return os.path.join(util.UserConfig().data['podcast_url'], self._course_path)

    @property
    def registration_date(self):
        """Get the formatted date from the parsed file.

        Returns:
            [str] - - the full date formatted in DD/MM/YYYY.

        """
        date = self._splitted_name[1]
        LOGGER.debug('registration date from file: %s', date)

        year, month, day = regex.sub(
            r'(\d{4})(\d{1,2})(\d{1,2})', r'\1 \2 \3', date).split(' ')
        LOGGER.debug('year, month, day: %s %s %s', year, month, day)

        month_name = util.convert_month_name()[month]
        complete_date = f'{day}/{month_name}/{year}'
        LOGGER.debug('formatted registration date: %s', complete_date)

        self.html_page['registration_date'] = complete_date

        return {"day": day, "month": month_name, "year": year}

    @property
    def teacher_name(self):
        """Get the full name of the teacher.

        Returns:
            [str] - - full name of the teacher abbreviation code.

        """
        short_name = '_'.join(self._splitted_name[2:4])
        LOGGER.debug('teacher name from file: %s', short_name)

        teacher_names = util.catalog_names("docenti")
        full_name = teacher_names[short_name]
        LOGGER.debug('teacher full name: %s', full_name)

        self.html_page['teacher_name'] = full_name
        return full_name

    @property
    def lesson_number(self):
        """Get the lesson string from the parsed file.

        Returns:
            [str] - - lesson number.

        """
        lesson, number = self._splitted_name[4:6]
        LOGGER.debug('lesson from file: %s', self._splitted_name[4:6])

        self.html_page['lesson'] = 'N.' + number

        formatted_lesson = f'{number}ª {lesson}'
        LOGGER.debug('formatted lesson: %s', formatted_lesson)

        return formatted_lesson

    @property
    def part_number(self):
        """Get the part string from the parsed file.

        Returns:
            [str] - - part number.

        """
        part = ' '.join(self._splitted_name[6:])
        LOGGER.debug('part from file: %s', part)

        LOGGER.debug('formatted part: \"%sª\"', part)
        return part + 'ª'

    @property
    def hash_name(self):
        """Create a hash name.

        Create a hash name for the file name that is going to be uploaded
        to the server.

        Returns:
            [str] - - full name of the file is going to be uploaded.

        """
        upload_name = '_'.join(self._splitted_name[4:])

        secret_token = hashlib.md5(
            self.name.encode('utf-8')).hexdigest()

        new_name = f'{upload_name}_{secret_token}.mp3'
        LOGGER.debug('uploading name: %s for %s', new_name, self.name)

        server_filepath = os.path.join(self.course_path, new_name)
        LOGGER.debug("server file path: %s", server_filepath)

        self.add_html_parts(
            {"server_path": self.course_path, "link": server_filepath})
        return new_name

    def add_html_parts(self, update_dict: dict):
        """Update html_page data with link and duration parts.

        Ads new dictionary to the part section of the existing dictionary.

        Argument:
            update_dict [dict] - a dictionary to add in class data dictionary.
        """
        part = ' '.join(self._splitted_name[-2:]).title()
        if self.html_page['parts'].get(part):
            self.html_page['parts'][part].update(update_dict)
        else:
            self.html_page['parts'].update({part: update_dict})

    def set_audio_intro(self):
        """Set the intro audio from the list in the catalog_names json file."""
        self.audio_intro = util.catalog_names()["intro"]
        LOGGER.debug("audio intro files: %s", self.audio_intro)

    @property
    def audio_intro(self) -> list:
        """Audio intro list to be merged with the podcast."""
        return self._audio_intro

    @audio_intro.setter
    def audio_intro(self, value):
        self.html_page['archive_name'] = '_'.join(
            self._splitted_name[:-2])
        date = self.registration_date
        const_dict = {
            "$VAR{course_name}": self.course_name,
            "$VAR{teacher_name}": self.teacher_name,
            "$VAR{lesson_number}": self.lesson_number,
            "$VAR{day}": date["day"],
            "$VAR{month}": date["month"],
            "$VAR{year}": date["year"],
            "$VAR{part_number}": self.part_number,
        }
        new_intro = []
        for audio in value:
            if audio in const_dict:
                new_intro.append(const_dict[audio])
            else:
                new_intro.append(audio)

        self._audio_intro = new_intro

    def _mkdir_tmp(self):
        """Create temporary directory.

        Create a temporary directory where to put the mp3 files created.
        Once the mp3 are merged, this directory should be delete.

        Returns:

            {str} - path like string of the tmp folder absolute path.

        """
        tmp_dir_path = f'{self.directory}/.tmp_{self.name}'
        LOGGER.debug('creating temporary folder: %s', tmp_dir_path)

        try:
            os.mkdir(tmp_dir_path)
        except FileExistsError:
            LOGGER.debug('tmp directory exists already')

        return tmp_dir_path

    def generate_podcast(self, bitrate='64k', sample_rate='22050', num_cuts='Auto'):
        """Generate final file to be uploaded to the server.

        Keyword Arguments:

            bitrate {str} - - specify bitrate(default: {'64k'})
            sample_rate {str} - - specify sample rate(default: {'22050'})
            num_cuts {str} - - how many cuts in audio(default: {Auto})
        """
        print("➡ num_cuts :", num_cuts)
        print("➡ sample_rate :", sample_rate)
        print("➡ bitrate :", bitrate)

        tmp_dir = self._mkdir_tmp()
        self.set_audio_intro()

        def _split_raw_podcast():
            watermark = util.catalog_names()["watermark"]
            LOGGER.debug("watermark audio: %s", watermark)

            podcast = pydub.AudioSegment.from_wav(self.abspath)

            if num_cuts == 'Auto':
                cuts = util.calculate_cuts(len(podcast))
            else:
                cuts = int(num_cuts)

            LOGGER.debug("splitting podcast in: [%s] parts", cuts)

            cut_each = math.ceil(len(podcast) / cuts)
            podcast_parts = podcast[::cut_each]

            n_parts = len(self._audio_intro)
            for part in podcast_parts:
                export_name = f"{tmp_dir}/{n_parts}-podcast-segment.wav"
                part.export(export_name, parameters=["-ar", sample_rate],
                            format="wav", bitrate=bitrate)

                self._audio_intro.append("podcast_segment")
                self._audio_intro.append(watermark)

                n_parts += 2

        def _copy_audio_intro():
            # """Copy the opening theme files from the audio library."""
            LOGGER.debug("Copying the audio intro files from the library")
            library = util.audio_library()
            for index, audio in enumerate(self._audio_intro):

                if audio == 'podcast_segment':
                    continue

                pad_fill = str(index).zfill(2)
                item_name = audio.replace(' ', '_') + '.mp3'
                item_name = item_name.lower()

                if item_name in library.keys():
                    src_file = os.path.join(library.get(item_name), item_name)
                    dst_name = f'{pad_fill}_{item_name}'

                    shutil.copy2(src_file, f'{tmp_dir}/{dst_name}')
                else:
                    self.missing_audio.add(item_name)

            err = True

            missing_files = list(self.missing_audio)

            for missing_audio in missing_files:
                file_name, _ = missing_audio.split('.')

                if util.generate_audio(text=file_name, path=util.USER_AUDIO):
                    self.missing_audio.remove(missing_audio)
                    err = False
                else:
                    LOGGER.warning(
                        'missing audio file for: %s', missing_audio)

            if not err:
                _copy_audio_intro()

        def _merge_audio():
            """Merge all the mp3 files from tmp folder."""
            LOGGER.info("merging all the audio files into the final file")
            # see pydub documentation of what is empty()
            podcast_segment = pydub.AudioSegment.empty()
            for sound in _create_audiosegment():
                podcast_segment += sound

            podcast_duration = util.audio_duration(len(podcast_segment))
            self.add_html_parts({"duration": podcast_duration})

            podcast_mp3_path = os.path.join(_mp3_path(), self.hash_name)
            podcast = podcast_segment.export(podcast_mp3_path,
                                             format="mp3",
                                             bitrate=bitrate,
                                             parameters=["-ar", sample_rate],
                                             # need more ide tags?
                                             tags={"album":
                                                   f"{self.course_name}",
                                                   "artist":
                                                   f"{self.teacher_name}"})
            shutil.rmtree(tmp_dir)
            self.add_html_parts({"path": podcast.name})
            LOGGER.debug('Final Podcast File: %s', podcast.name)

        def _create_audiosegment():
            """Create pydub audio segment from all the mp3 files in tmp dir."""
            path = pathlib.Path(tmp_dir).iterdir()
            LOGGER.debug('combining audio files in folder: %s', tmp_dir)
            for item in sorted(path):
                if regex.search(r'(\.mp3|\.wav)$', str(item)):
                    LOGGER.debug('merging audio: %s', os.path.basename(item))
                    yield pydub.AudioSegment.from_file(str(item))

        def _mp3_path() -> str:
            """Get the mp3 folder path."""
            mp3_path = pathlib.Path(self.abspath).parent / 'mp3'
            if not mp3_path.exists():
                LOGGER.debug("mp3 folder not found...creating one.")
                os.mkdir(mp3_path)
            LOGGER.debug("mp3 folder path: %s", mp3_path)
            return mp3_path

        _split_raw_podcast()
        _copy_audio_intro()
        _merge_audio()


def generate_html(html_data, test_env=False):
    """Generate html page using yattag module.

    Arguments:
        html_data - [dict] - a dictionary with all the information
        from the generated podcast.
        test_env - [bool] - if True then changes path on html file to test path

    """
    LOGGER.debug('generating html page info from dict: %s', html_data)
    doc, tag, text = yattag.Doc().tagtext()
    doc.stag('hr')

    with tag('div', klass='virgil_podcast_info'):

        with tag('span', klass='virgil_description'):
            text('Docente:')
        with tag('span', klass='virgil_credentials'):
            text(html_data['teacher_name'])
        doc.stag('br')

        with tag('span', klass='virgil_description'):
            text('Data:')
        with tag('span', klass='virgil_credentials'):
            text(html_data['registration_date'])
        doc.stag('br')

        with tag('span', klass='virgil_description'):
            text('Lezione:')
        with tag('span', klass='virgil_credentials'):
            text(html_data['lesson'])

        doc.stag('hr')

        with tag('div', klass='virgil_podcast_part'):

            for part_num, part_info in sorted(html_data['parts'].items()):
                with tag('p'):
                    text(f'{part_num} | Durata {part_info["duration"]}')

                if util.UserConfig().value('html_mediaplayer'):
                    with tag('object', id="audioplayer1",
                             width="290", height="24",
                             data=util.UserConfig().data['plugin_url'],
                             type="application/x-shockwave-flash"):
                        doc.stag('param', name="FlashVars",
                                 value=f"playerID=1&soundFile={part_info['link']}")

                with tag('a', "download", href=part_info["link"], target='_blank'):
                    with tag('button', klass='virgil_button'):
                        text('Download')

    def test_path(text):
        """Substitute the current path with the test path."""
        sub_path = regex.compile(
            r"(?<=didattica/)PODCAST/[A-Z]{3}/[A-Z]{3,}(?=/Lezione)")
        sub = sub_path.sub("virgil_test", text)
        return sub

    def generate_archive(text):
        """Create a html file archive for later use."""
        today = datetime.today().strftime('%m.%d.%Y_%H:%M_')
        podcast_name = html_data['archive_name']
        file_path = os.path.join(
            util.get_path('archive'), today + podcast_name + '.html')
        LOGGER.debug('creating html archive: %s', file_path)
        with open(file_path, 'w') as file:
            if test_env:
                text = test_path(text)
            file.write(text)

    page = yattag.indent(doc.getvalue())
    LOGGER.debug('html page generated')
    generate_archive(page)


if __name__ == '__main__':
    pass
