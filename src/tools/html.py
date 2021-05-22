import re
import os
import logging

from datetime import datetime

import yattag

from src.util import UserConfig
from src.startup import PATH_PACKAGE

LOGGER = logging.getLogger('podcasttool.html')


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

                settings = UserConfig()
                if settings.value('html_mediaplayer', False):
                    with tag('object', id="audioplayer1",
                             width="290", height="24",
                             data=settings.value('plugin_url'),
                             type="application/x-shockwave-flash"):
                        doc.stag('param', name="FlashVars",
                                 value=f"playerID=1&soundFile={part_info['link']}")

                with tag('a', "download", href=part_info["link"], target='_blank'):
                    with tag('button', klass='virgil_button'):
                        text('Download')

    def generate_archive(text):
        """Create a html file archive for later use."""
        today = datetime.today().strftime('%m.%d.%Y_%H:%M')
        podcast_name = html_data['archive_name']
        html_file = f'{today}_{podcast_name}.html'

        file_path = os.path.join(PATH_PACKAGE, 'archive', html_file)
        LOGGER.debug('creating html archive: %s', file_path)

        with open(file_path, 'w') as file:
            if test_env:
                text = _test_path(text)
            file.write(text)

    page = yattag.indent(doc.getvalue())
    LOGGER.debug('html page generated')

    generate_archive(page)


def _test_path(text):
    """Substitute the current path with the test path."""
    text = re.sub(r'PODCAST\/[A-Z]{3}\/[A-Z]{3}\w{1,2}', 'virgil_test', text)
    return text


if __name__ == '__main__':
    p = 'https://www.fonderiesonore.com/images/didattica/PODCAST/ALP/SECD/Lezione_4_Parte_1_530835b734b492344ee2f2dca5b76244.mp3'
    x = test_path(p)
    print(x)
