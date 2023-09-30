import os
import re
import logging
from datetime import datetime

from ..utils import UserConfig
from ..startup import USER_ARCHIVE

LOGGER = logging.getLogger('podcasttool.html')


def generate_html(html_data, test_env=False):
    settings = UserConfig()

    credentials = f"""
    <span class="virgil_description">Docente:</span>
    <span class="virgil_credentials">{html_data['teacher_name']}</span>
    <br />
    <span class="virgil_description">Data:</span>
    <span class="virgil_credentials">{html_data['registration_date']}</span>
    <br />
    <span class="virgil_description">Lezione:</span>
    <span class="virgil_credentials">{html_data['lesson']}</span>
    <hr />
    """

    body = ""

    for part_num, part_info in sorted(html_data['parts'].items()):
        body += f"<p>{part_num} | Durata {part_info['duration']}</p>"

        if settings.value('html_mediaplayer', False):
            body += f"""
                <object id="audioplayer1" width="290" height="24" 
                    data="{settings.value('plugin_url')}" 
                    type="application/x-shockwave-flash">
                        <param name="FlashVars"
                        value="playerID=1&amp;soundFile={part_info['link']}">
                </object>
                """

        body += f"""
            <a download href="{part_info['link']}" target="_blank">
                <button class="virgil_button">Download</button>
            </a>
            """

    page = f"""
    <hr />
    <div class="virgil_podcast_info">
        {credentials}
        <div class="virgil_podcast_part"> 
            {body}
        </div>
    </div>
    """

    LOGGER.debug('html page generated')

    _generate_archive(html_data['archive_name'], page, test_env)

    return page


def _generate_archive(filename, text, test_env):
    """Create a html file archive for later use."""

    today = datetime.today().strftime('%m%d%Y_%H%M')
    file_path = os.path.join(USER_ARCHIVE, f"{today}_{filename}.html")
    LOGGER.debug('creating html archive: %s', file_path)

    with open(file_path, 'w') as file:
        if test_env:
            text = _test_path(text)
        file.write(text)


def _test_path(text):
    """Substitute the current path with the test path."""
    text = re.sub(r'PODCAST\/[A-Z]{3}\/[A-Z]{3}\w{1,2}', 'virgil_test', text)
    return text


if __name__ == '__main__':
    p = 'https://www.fonderiesonore.com/images/didattica/PODCAST/ALP/SECD/Lezione_4_Parte_1_530835b734b492344ee2f2dca5b76244.mp3'
    x = test_path(p)
    print(x)
