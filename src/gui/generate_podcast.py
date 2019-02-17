"""Podcast generator for Fonderie Sonore."""
import os
import math
import json
import wave
import ftplib
import shutil
import hashlib
import pathlib
import logging
import datetime

import pydub
import regex
import yattag
import tinytag

import utility


LOGGER = logging.getLogger('podcast_tool.generate_podcast')


class PodcastParser(object):
    """Take podcast file name ad extract indexes based string.

    Example indexes based on the code name:
    SEC6_20133201_E_Cosimi_Lezione_4_Parte_1.wav
        codice_Catalogo         =  0     | (SEC6)
        date                    =  1     | (20133201)
        short_name              =  2 + 3 | (E_Cosimi)
        numero_lezione          =  4 + 5 | (Lezione_4)
        numero_parte.wav        =  6 + 7 | (Parte_1.wav)
    """

    html_page_info = {}

    def __init__(self, podcast_path: str):
        """Construct method for the PodcastParser class.

        Arguments:
            podcast_path {string} -- full path like string of the podcast file.

        """
        LOGGER.debug('Initialize PodcastParser class ->')

        # extract name from full path
        filename, _ = os.path.splitext(os.path.basename(podcast_path))
        self._podcast_file = filename

        # podcast names have always this structure:
        # ex: SEC6_20133201_E_Cosimi_Lezione_4_Parte_1.wav
        self._podcast_splitted = self._podcast_file.split('_')

        self.html_page_info['archive_name'] = '_'.join(
            self._podcast_splitted[:-2])

        LOGGER.debug(f'podcast name splitted: {self._podcast_splitted}')

        # absolute path of the file
        self._podcast_abs_path = podcast_path
        LOGGER.debug(f'podcast file absolute path: {self._podcast_abs_path}')

        # directory of the file
        self._podcast_directory = os.path.dirname(podcast_path)
        LOGGER.debug(f'podcast file directory: {self._podcast_directory}')

    @property
    def get_filename(self):
        """Return string representation of the file name."""
        return str(self._podcast_file)

    @property
    def abs_path(self):
        """Return string representation of the absolute path of the file."""
        return str(self._podcast_abs_path)

    @property
    def file_directory(self):
        """Return string representation of the directory of the file."""
        return str(self._podcast_directory)

    def __str__(self):
        """Return podcast file name."""
        return f'{os.path.basename(self._podcast_abs_path)}'

    def __repr__(self):
        """Return creation podcast class."""
        return f'PodcastParser("{self._podcast_abs_path}")'

    @property
    def course_name(self):
        """Get the full course name of the parsed file.

        Returns:
            [str] -- the full name of the course name.

        """
        # the code is always the first 3 strings in the name
        code = self._podcast_splitted[0]
        LOGGER.debug(f'course code from file: {code}')

        # for parsing pursoses I need to deattache the edition
        course_code, edition = regex.sub(
            r'([A-Z]{3})([A-Z]{1,3})', r'\1 \2', code).split(' ')

        LOGGER.debug(f'codice corso, edizione: {course_code, edition}')

        course_catalog = utility.catalog_names()['corsi']
        # course_catalog = self._catalog_names()['corsi']

        course_info = course_catalog[course_code]

        course = course_info['course_name']
        LOGGER.debug(f'get complete course name: {course}')

        self.html_page_info['course_name'] = course

        return course

    @property
    def registration_date(self):
        """Get the formatted date from the parsed file.

        Returns:
            [str] -- the full date formatted in DD/MM/YYYY.

        """
        date = self._podcast_splitted[1]
        LOGGER.debug(f'registration date from file: {date}')

        year, month, day = regex.sub(
            r'(\d{4})(\d{1,2})(\d{1,2})', r'\1 \2 \3', date).split(' ')
        LOGGER.debug(f'year, month, day: {year, month, day}')

        # date in numeric form 12.12.2012 (if needed)
        # numeric_date = f'{day}/{month}/{year}'

        month_name = self._convert_month_name()[month]
        complete_date = f'{day}/{month_name}/{year}'
        LOGGER.debug(f'formatted registration date: {complete_date}')

        self.html_page_info['registration_date'] = complete_date

        return complete_date

    @property
    def teacher_name(self):
        """Get the full name of the teacher.

        Returns:
            [str] -- full name of the teacher abbreviation code.

        """
        short_name = '_'.join(self._podcast_splitted[2:4])
        LOGGER.debug(f'teacher name from file: {short_name}')

        teacher_catalog = utility.catalog_names()['docenti']
        # teacher_catalog = self._catalog_names()['docenti']
        full_name = teacher_catalog[short_name]
        LOGGER.debug(f'teacher full name: {full_name}')

        self.html_page_info['teacher_name'] = full_name
        return full_name

    @property
    def lesson_number(self):
        """Get the lesson string from the parsed file.

        Returns:
            [str] -- lesson number.

        """
        lesson, number = self._podcast_splitted[4:6]
        LOGGER.debug(f'lesson from file: {self._podcast_splitted[4:6]}')

        self.html_page_info['lesson'] = 'N.' + number

        formatted_lesson = f'{number}ª {lesson}'
        LOGGER.debug(f'formatted lesson: {formatted_lesson}')

        return formatted_lesson

    @property
    def part_number(self):
        """Get the part string from the parsed file.

        Returns:
            [str] -- part number.

        """
        part = ' '.join(self._podcast_splitted[6:])
        LOGGER.debug(f'part from file: {part}')

        LOGGER.debug(f'formatted part: \"{part}ª\"')
        return part + 'ª'

    @staticmethod
    def _convert_month_name():
        """Convert month number value to italian month name."""
        month_dict = {
            '01': 'Gennaio',
            '02': 'Febbraio',
            '03': 'Marzo',
            '04': 'Aprile',
            '05': 'Maggio',
            '06': 'Giugno',
            '07': 'Luglio',
            '08': 'Agosto',
            '09': 'Settembre',
            '10': 'Ottobre',
            '11': 'Novembre',
            '12': 'Dicembre'
        }
        return month_dict


class PodcastGenerator(PodcastParser):
    """Generate the podcast phisycal file.

    Create the podcast file that is going to be uploaded to the server
    by combining the wav registration and the audio cues from the library.
    """

    uploading_list = []
    html_durata_podcast = {}

    def __init__(self, audio_file: str, *args,
                 bitrate='64k', sample_rate='44100', watermarks=''):
        """Parse and create the podcast file."""
        super().__init__(audio_file)

        self.audio_file = audio_file
        day, month, year = self.registration_date.split('/')

        self._opening_theme = [
            'Fonderie_Sonore_Podcast',
            'Materiale_riservato_agli_studenti_della_scuola',
            'Corso:',
            self.course_name,
            'Docente:',
            self.teacher_name,
            'Podcast audio della:',
            self.lesson_number,
            'Del:',
            day,
            month,
            year,
            self.part_number,
        ]

        if not self._check_already_created():
            self.custom_bitrate = bitrate
            self.custom_sample_rate = sample_rate

            if watermarks:
                self.watermark_number = watermarks + 1
            else:
                self.watermark_number = self._calculate_cuts(self.__len__())

            self.tmp_dir = self._tmp_dir()
            self._split_podcast()
            self._create_theme()
            self._merge_audio()
        else:
            LOGGER.debug(f'podcast already created')

    def _mp3_path(self) -> str:
        """Get the mp3 folder path."""
        mp3_path = pathlib.Path(self.audio_file).parent / 'mp3'
        LOGGER.debug(f'mp3_path: {mp3_path}')
        return mp3_path

    def _check_already_created(self):
        """Check if mp3 file already exists.

        If mp3 file already exstis, means that probably there were some
        errors in the uploading to the server, thus restarting the script will
        avoid going to the process of re-creating the podcast from scratch
        and instead directly jumping to the uploading process.
        """
        podcast_mp3 = os.path.join(self._mp3_path(), self.create_hash_name)
        if os.path.exists(podcast_mp3):
            self.uploading_list.append(podcast_mp3)

            # get lenght of mp3 file in milliseconds
            mp3_duration = tinytag.TinyTag.get(podcast_mp3).duration * 1000
            self._audio_duration(mp3_duration)
            return True
        return False

    def __len__(self):
        """Get the lenght of the audio in milliseconds.

        Returns:
            int -- return in ms of the lenght audio

        """
        try:
            with wave.open(self.audio_file, 'rb') as wave_file:
                nframe = wave_file.getnframes()
                rframe = wave_file.getframerate()
        except Exception as error:
            LOGGER.critical(f'{error} - probably not a wave file!')
            exit()

        # amount in seconds
        total_float_seconds = nframe / rframe
        total_ms = math.ceil(total_float_seconds * 1000)

        LOGGER.debug(f'total float duration in seconds: {total_float_seconds}')
        LOGGER.debug(f'total integer duration in ms: {total_ms}')

        return total_ms

    @staticmethod
    def _calculate_cuts(ms_time: int) -> int:
        """Calculate the numbers of audio cuts based on the audio lenght.

        Returns:
            [int] -- how many watermark to put in the podcast.

        """
        two_hours = 7_200_000
        one_hour = 3_600_000

        if ms_time > two_hours:
            return 5
        if ms_time < two_hours and ms_time > one_hour:
            return 4
        if ms_time < one_hour:
            return 3

    # @utility.profile
    def _split_podcast(self):
        """Cut the podcast file into n number of segments.

        Between each new cut there is going to be a "watermark" type of audio.

        TODO: currently the cuts are based on total duration of the audio
        divide by n. Thus is likely that the cuts are going to be in te middle
        of words. Want to be able to detect silence and cut only there.
        """
        song = pydub.AudioSegment.from_file(self.audio_file)
        LOGGER.debug(f'initialize pydub AudioSegment: {song}')

        LOGGER.debug(f'podcast ms duration: {self.__len__()}')
        LOGGER.debug(f'podcast seconds duration: {self.__len__() / 1000}')
        LOGGER.debug(f'adding watermarks n.: {self.watermark_number}')

        cut_each = math.ceil(self.__len__() / self.watermark_number)

        # for logging only
        cuts_in_seconds = datetime.timedelta(milliseconds=cut_each).seconds
        LOGGER.debug(f'cut every: {cuts_in_seconds} seconds | {cut_each} ms')

        song_parts = song[::cut_each]

        LOGGER.debug(f'lenght opening theme files: {len(self._opening_theme)}')

        watermark = self._opening_theme[1]
        watermark_n = 0
        LOGGER.debug(f'watermark: {watermark}')

        for part in song_parts:
            export_name = f'{len(self._opening_theme)}_Ppart_{watermark_n}.mp3'

            part.export(f'{self.tmp_dir}/{export_name}',
                        parameters=["-ar", self.custom_sample_rate],
                        format='mp3', bitrate=self.custom_bitrate)

            LOGGER.debug(f'exporting podcast: {export_name}')
            LOGGER.debug(f'adding watermark: {watermark}.mp3')

            # I need to append 'podcast part' because I need
            # all the items  the list to be in cronological order
            # once I copy the files from the library
            self._opening_theme.append('podcast part')
            if watermark_n < self.watermark_number - 1:
                self._opening_theme.append(watermark)

            watermark_n += 1

    def _create_theme(self):
        """Copy the opening theme files from the audio library."""
        library = self.audio_library()
        for item in enumerate(self._opening_theme):

            pad_fill = str(item[0]).zfill(2)
            item_name = item[1].replace(' ', '_') + '.mp3'

            if item_name in library.keys():
                src_file = os.path.join(library.get(item_name), item_name)
                dst_name = f'{pad_fill}_{item_name}'

                shutil.copy2(src_file, f'{self.tmp_dir}/{dst_name}')

    def _check_files(self):
        """Check if all files have been copied. if not exit."""
        LOGGER.debug(f'merging audio files in folder: {self._tmp_dir}')

        list_dir = os.listdir(self.tmp_dir)
        if len(list_dir) < len(self._opening_theme):
            error = 'something went wrong. I found only', len(
                list_dir), 'files instead of ', len(self._opening_theme)
            LOGGER.warning(f'error: {error}')
            exit()

    @staticmethod
    def audio_library():
        """Create a dictionary with all the files from the library.

        Returns:
            [dict] -- dictionary with key as files names and values as paths

        """
        library_path = utility.get_path('audio_library')
        library_dict = {}
        for dirpath, _, filenames in os.walk(library_path):
            for filename in filenames:
                if filename.endswith('mp3'):
                    library_dict[filename] = dirpath
        return library_dict

    @property
    def create_hash_name(self):
        """Create a hash name.

        Create a hash name for the file name that is going to be uploaded
        to the server.

        Returns:
            [str] -- full name of the file is going to be uploaded.

        """
        upload_name = '_'.join(self._podcast_splitted[4:])

        secret_token = hashlib.md5(
            self.get_filename.encode('utf-8')).hexdigest()

        new_name = f'{upload_name}_{secret_token}.mp3'
        LOGGER.debug(f'uploading name: {new_name}')

        return new_name

    def _tmp_dir(self):
        """Create temporary directory.

        Create a temporary directory where to put the mp3 files created.
        Once the mp3 are merged this directory should be delete.

        Returns:
            {str} -- path like string of the tmp folder absolute path.

        """
        # folder_name, file_ext = os.path.splitext(self._podcast_file)
        tmp_folder_path = f'{self.file_directory}/.tmp_{self.get_filename}'
        LOGGER.debug(f'creating temporary folder: {tmp_folder_path}')
        try:
            os.mkdir(tmp_folder_path)
        except FileExistsError:
            LOGGER.warning(f'tmp folder exists already ')

        return tmp_folder_path

    def _create_audiosegment(self):
        """Create pydub audio segment from all the mp3 files in tmp dir."""
        path = pathlib.Path(self.tmp_dir).glob('*mp3')
        for item in sorted(path):
            LOGGER.debug(f'merging audio: {item}')
            yield pydub.AudioSegment.from_file(str(item))

    # @profile
    def _merge_audio(self):
        """Merge all the mp3 files from tmp folder into the final podcast."""
        # see pydub documentation of what is empty()
        podcast_segment = pydub.AudioSegment.empty()
        for sound in self._create_audiosegment():
            podcast_segment += sound

        # creating the name of the file that is going to be uploaded
        podcast_mp3_path = os.path.join(self.tmp_dir, self.create_hash_name)

        # TODO: check if are better ways of handling the duration
        self._audio_duration(len(podcast_segment))

        # need more ide tags?
        end_file = podcast_segment.export(podcast_mp3_path,
                                          format="mp3",
                                          bitrate=self.custom_bitrate,
                                          parameters=[
                                              "-ar", self.custom_sample_rate],
                                          tags={"album": f"{self.course_name}",
                                                "artist": f"{self.teacher_name}"},)
        LOGGER.debug(f'Final Podcast File: {end_file.name}')

        self._move_and_delete(end_file.name)

    # @property
    def _audio_duration(self, file_lenght: int) -> str:
        """Get the formatted duration of an audio file.

        Arguments:
            [int] -- lenght of the audio in milliseconds
        Returns:
            [str] -- the full duration of the podcast file in H/M/S
        """
        song_duration = str(datetime.timedelta(milliseconds=file_lenght))

        format_duration = regex.sub(
            r'^(\d{1,2}):(\d\d):(\d\d).+', r'\1h \2m \3s', song_duration)

        part = ' '.join(self._podcast_splitted[-2:]).title()

        self.html_durata_podcast[part] = [format_duration]
        self.html_page_info['audio_parts'] = self.html_durata_podcast

        LOGGER.debug(f'lista durata podcast: {self.html_durata_podcast}')
        return format_duration

    def _move_and_delete(self, file_path: str) -> str:
        mp3_path = shutil.move(file_path, self._mp3_path())
        self.uploading_list.append(mp3_path)

        shutil.rmtree(pathlib.Path(file_path).parent)

        return mp3_path


class ServerUploader:
    """Upload podcast files to server.

    Uploading podcast files to server with the ftplib module.
    """

    uploading_list = []

    def __init__(self, uploading_file, test_mode=''):
        """Upload podcast to server."""
        self.uploading_file = uploading_file
        self.test_mode = test_mode
        try:
            self.upload_to_server()
        except Exception as error:
            LOGGER.critical(
                f'Problemi a caricare file: {error} {self.uploading_file}')

    def __str__(self):
        return os.path.basename(self.uploading_file)

    def __repr__(self):
        return f'{__class__.__name__}("{self.uploading_file}")'

    def __len__(self):
        """Return the file size in megabytes."""
        file_size_mb = os.stat(self.uploading_file).st_size // 1_000_000
        return file_size_mb

    def upload_to_server(self):
        """Upload podcast file to server."""
        # virgil_test = self._server_credentials()['virgil_test']
        virgil_test = os.environ['FONDERIE_VIRGILTEST']

        server_p = self.server_path if not self.test_mode else virgil_test

        self.uploading_list.append(
            "http://" + os.path.join(server_p, self.__str__()))

        with ftplib.FTP(os.environ['FONDERIE_HOST'],
                        os.environ['FONDERIE_USER'],
                        os.environ['FONDERIE_PASSWORD']) as ftp:
        # with ftplib.FTP(self._server_credentials()['host'],
        #                 self._server_credentials()['user'],
        #                 self._server_credentials()['password']) as ftp:
            try:
                ftp.cwd(server_p)
            except ftplib.error_perm:
                LOGGER.debug(f'creating directory: {server_p}')
                ftp.mkd(server_p)
                ftp.cwd(server_p)

            with open(self.uploading_file, 'rb') as upload:
                print('<-uploading->', )
                print('uploading_file:', self.uploading_file, 'in:', ftp.pwd())

                # XXX COMMENT THIS LINE OUT FOR TESTING -> NO UPLOAD <-
                # status = ftp.storbinary(f'STOR {self.__str__()}', upload)
                # LOGGER.debug(f'status: {status}')

    @property
    def server_path(self):
        """Extract root course name from file path and create server path."""
        file_path = pathlib.Path(self.uploading_file)
        root_folder = '/'.join(file_path.parent.parts[-3:-1])
        server_path = os.environ['FONDERIE_PODCAST'] + root_folder
        # server_path = self._server_credentials()['podcast_path'] + root_folder
        return server_path

    # @staticmethod
    # def _server_credentials():
    #     """Parse json file for server credentials."""
    #     # TODO: need to check if on linux the .env file works
    #     json_file = os.path.join(os.path.dirname(
    #         __file__), '.server_credentials.json')
    #     with open(json_file) as file:
    #         server_dict = json.load(file)['fonderie']
    #     return server_dict


class HtmlGenerator:
    def __init__(self, html_data: dict):
        self.html_data = html_data

        self.generate_page()

    def generate_page(self):
        """Generate html page using yattag module."""
        doc, tag, text = yattag.Doc().tagtext()
        doc.stag('hr')

        with tag('div', klass='virgil_podcast_info'):

            with tag('span', klass='virgil_description'):
                text('Docente:')
            with tag('span', klass='virgil_credentials'):
                text(self.html_data['teacher_name'])
            doc.stag('br')

            with tag('span', klass='virgil_description'):
                text('Data:')
            with tag('span', klass='virgil_credentials'):
                text(self.html_data['registration_date'])
            doc.stag('br')

            with tag('span', klass='virgil_description'):
                text('Lezione:')
            with tag('span', klass='virgil_credentials'):
                text(self.html_data['lesson'])

            doc.stag('hr')

            with tag('div', klass='virgil_podcast_part'):

                for part in sorted(self.html_data['audio_parts'].items()):
                    with tag('h3'):
                        text(f'{part[0]} | Durata {part[1][0]}')

                    with tag('object', id="audioplayer1",
                             width="290", height="24",
                             data="http://www.fonderiesonore.it/plugins/content/1pixelout/player.swf",
                             type="application/x-shockwave-flash"):
                        doc.stag('param', name="FlashVars",
                                 value=f"playerID=1&soundFile={part[1][1]}")

                    with tag('a', "download", href=part[1][1], target='_blank'):
                        with tag('button', klass='virgil_button'):
                            text('Download')

        page = yattag.indent(doc.getvalue())
        self.write_archive(page)

    def create_archive_path(self):
        """Create a html file archive for later use."""
        today = datetime.datetime.today().strftime('%m.%d.%Y_%H:%M_')
        podcast_name = self.html_data['archive_name']
        print(f'--> DEBUG podcast_name: {podcast_name} <--')
        file_path = os.path.join(
            utility.get_path('archive'), today + podcast_name + '.html')
        return file_path

    def podcast_file(self):
        podcast_path = self.create_archive_path()
        return podcast_path

    def write_archive(self, text: str):
        """Write a html file with the podcast information."""
        with open(self.podcast_file(), 'w') as file:
            file.write(text)


def run_gui1(podcast_list: list, *args, **audio_options) -> str:
    """Run main app."""
    print(audio_options)
    for file in podcast_list:
        podcast = PodcastGenerator(file, **audio_options)

    podcast_list = podcast.uploading_list
    html_data = podcast.html_page_info

    for file in podcast_list:
        ServerUploader(file)

    # virgil_test = [os.environ['TEST_LEZIONE_1'],
        # os.environ['TEST_LEZIONE_2'],
        # os.environ['TEST_LEZIONE_3']]
    # adding the server path of the uploaded files to the html a href tag
    [_[0].append(_[1]) for _ in zip(html_data['audio_parts'].values(),
                                    ServerUploader.uploading_list)]
    return HtmlGenerator(html_data).podcast_file()


# def run_gui(podcast_list: list, *args, **audio_options) -> str:
#     """Run main app."""
#     # for file in podcast_list:
#     podcast = PodcastGenerator(podcast_list, **audio_options)

#     podcast_list = podcast.uploading_list
#     html_data = podcast.html_page_info
#     LOGGER.warning(f'html_data: {html_data}')
#     LOGGER.warning(f'podcast_list: {podcast_list}')

#     exit('-> exit')
#     for file in podcast_list:
#         ServerUploader(file)

#     # virgil_test = [os.environ['TEST_LEZIONE_1'],
#         # os.environ['TEST_LEZIONE_2'],
#         # os.environ['TEST_LEZIONE_3']]
#     # adding the server path of the uploaded files to the html a href tag
#     [_[0].append(_[1]) for _ in zip(html_data['audio_parts'].values(),
#                                     ServerUploader.uploading_list)]
#     return HtmlGenerator(html_data).podcast_file()


if __name__ == '__main__':
    pass
