import os
import sys
import gtts
import json


def override(func):
    def inner(*args, **kwargs):
        if kwargs['override']:
            func()
    return inner


PATH_RESOURCES = os.path.dirname(os.path.dirname(__file__))
print("➡ PATH_PACKAGE :", PATH_RESOURCES)

# PATH_RESOURCES = os.path.join(PATH_PACKAGE, 'resources')
PATH_AUDIO = os.path.join(PATH_RESOURCES,  'audio')


def catalog_names() -> str:
    """Open json catalog of names to grab the teachers and courses names."""

    catalog = os.path.join(PATH_RESOURCES, 'data', 'catalog.json')
    with open(catalog) as f:
        json_data = json.load(f)
        return json_data


@override
def generate_docenti(override=False):
    """Generate the teachers name audio cue.

    Keyword Arguments:
        override {bool} -- if True, overrides existing audio (default: {False})
    """
    fp = 'docenti'
    delete_old(fp)

    docenti = catalog_names()['docenti']
    print('Docenti: ')

    for nome_docente in docenti.values():
        filename_docenti = nome_docente.replace(' ', '_')
        try:
            import _textblob

            check_lang = textblob.TextBlob(nome_docente).detect_language()
            print(nome_docente,  '-> language: ', check_lang)

            generate_audio(text=nome_docente, filename=filename_docenti,
                           rel_path=fp, lang=check_lang)
        except (ValueError, ModuleNotFoundError) as err:
            print(nome_docente)
            generate_audio(text=nome_docente, filename=filename_docenti,
                           rel_path=fp)


@override
def generate_corsi(override=False):
    """Generate the courses name audio cues.

    Keyword Arguments:
        override {bool} -- if True, overrides existing audio (default: {False})
    """
    fp = 'corsi'
    delete_old(fp)

    corsi = catalog_names()['corsi']
    print('Corsi: ')

    for corso in corsi.values():
        nome_corso = corso['course_name']
        try:
            import textblob
            check_lang = textblob.TextBlob(nome_corso).detect_language()
            print(nome_corso, ' -> language: ', check_lang)
            generate_audio(text=nome_corso, filename=nome_corso,
                           rel_path=fp, lang=check_lang)
        except (ValueError, ModuleNotFoundError):
            print(nome_corso)
            generate_audio(text=nome_corso, filename=nome_corso,
                           rel_path=fp)


@override
def generate_other(override=False):
    """Generate other audio cues.

    Fonderie Sonore Podcast.
    Materiale riservato agli studenti della scuola.
    Podcast audio della, Corso, Docente, Del, Parte, Lezione

    Keyword Arguments:
        override {bool} -- if True, overrides existing audio (default: {False})
    """
    fp = 'misc'
    delete_old(fp)

    mix_phrases = ['Fonderie Sonore Podcast', 'Podcast',
                   'Materiale riservato agli studenti della scuola',
                   'Podcast audio della:',
                   'Corso:', 'Docente:', 'Del:',
                   'Lezione', 'Parte:']
    print('Other: ')
    for phrase in mix_phrases:
        print(phrase)
        filename_phrase = phrase.replace(':', '')
        generate_audio(
            text=phrase, filename=filename_phrase, rel_path=fp)


@override
def generate_lesson_part(override=False):
    """Generate parte 1 parte 2 lezione 1 lezione as a whole word.
    1ª Lezione
    2ª Lezione
    ...
    Parte 1ª
    Parte 2ª
    ...
    Keyword Arguments:
        override {bool} -- if True, overrides existing audio (default: {False})
    """
    fp = 'lesson_part'
    delete_old(fp)

    for phrase in ['parte', 'Lezione']:
        for i in range(1, 20):
            if phrase == 'parte':
                text = f'{phrase} {i}ª'
                print(text)
                generate_audio(text=text, filename=text, rel_path=fp)
            elif phrase == 'Lezione':
                text = f'{i}ª {phrase}'
                generate_audio(text=text, filename=text, rel_path=fp)
                print(text)


@override
def generate_numeri(override=False):
    """Generate ordinal numeric audio cues (1th, 2nd, 3rd).

    Keyword Arguments:
        override {bool} -- if True, overrides existing audio (default: {False})
    """

    fp = 'numeri'
    delete_old(fp)
    print('Numeri: ')

    for numero in range(1, 32):
        print(numero, 'ª')
        nome_numero = str(numero) + 'ª'
        file_name = nome_numero.zfill(2)
        generate_audio(text=nome_numero, filename=file_name, rel_path=fp)


def generate_data(override_all=False, override_giorni=False,
                  override_mesi=False, override_anni=False):
    """Generate numeric date audio cue.

    Keyword Arguments:
        override_all {bool} - - if True, overrides ALL existing audio(default: {False})
        override_giorni {bool} - - if True, overrides ONLY giorni existing audio(default: {False})
        override_mesi {bool} - - if True, overrides ONLY mesi existing audio(default: {False})
        override_anni {bool} - - if True, overrides ONLY anni existing audio(default: {False})
    """
    def generate_giorni():
        fp = 'data/giorni'
        if override_all or override_giorni:
            delete_old(fp)
            print('Giorni: ')
            for giorno in range(1, 32):
                giorno_nome = str(giorno)
                file_name = f'{str(giorno).zfill(2)}'
                generate_audio(text=giorno_nome,
                               filename=file_name, rel_path=fp)
                print(giorno)

    def generate_mesi():
        fp = 'data/mesi'
        if override_all or override_mesi:
            delete_old(fp)
            mesi = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile',
                    'Maggio', 'Giugno', 'Luglio', 'Agosto',
                    'Settembre', 'Ottobre', 'Novembre', 'Dicembre']
            print('Mesi: ')
            n = 1
            for mese in mesi:
                generate_audio(text=mese, filename=mese, rel_path=fp)
                n += 1
                print(mese)

    def generate_anni():
        fp = 'data/anni'
        if override_all or override_anni:
            delete_old(fp)
            print('Anni: ')
            for anno in range(2018, 2031):
                generate_audio(text=anno, filename=str(anno), rel_path=fp)
                print(anno)

    generate_giorni()
    generate_mesi()
    generate_anni()


def generate_audio(text, filename, rel_path, lang='it'):
    """Generate the audio cues.

    Arguments:
        text {str} - what is going to be spoke in the audio cue.
        file_name {str} - the name of the saved file.
        rel_path {str} - relative path of where to save the file.

    Keyword Arguments:
        lang {str} - the language for the audio(default: 'it')
    """
    speak = gtts.gTTS(text=str(text), lang=lang)
    filename = filename.replace(' ', '_')
    file = os.path.join(PATH_AUDIO, rel_path, f'{filename}.mp3'.lower())
    speak.save(file)


def delete_old(path):
    """Delete old audio files if overriding.

    Arguments:
        path {string} - - path like string for the directory in where to delete.
    """
    audio_path = os.path.join(PATH_AUDIO, path)
    os.makedirs(audio_path, exist_ok=True)

    for item in os.listdir(audio_path):
        file_path = os.path.join(audio_path, item)
        os.remove(file_path)


if __name__ == '__main__':
    # generate_docenti(override=True)
    # generate_corsi(override=True)
    # generate_other(override=True)
    # generate_lesson_part(override=True)
    # generate_numeri(override=True)
    # generate_data(override_all=True, override_giorni=True,
    #               override_mesi=True, override_anni=True)
