import os
import gtts
import json
import regex
import textblob


def catalog_names() -> str:
    """Open json catalog of names to grab the teachers and courses names."""
    # json file should always be in
    # the same directory of where the src code is
    json_file = '/Users/virgilsisoe/.venvs/PodcastTool/src/gui/catalog_names.json'
    try:
        with open(json_file) as f:
            json_data = json.load(f)
            return json_data
    except FileNotFoundError:
        print('no json file found!', json_file)
        exit()


def generate_docenti(override=False):
    """Generate the teachers name audio cue.

    Keyword Arguments:
        override {bool} -- if True, overrides existing audio (default: {False})
    """
    fp = 'audio_library/docenti/'
    if override:
        delete_old(fp)
        docenti = catalog_names()['docenti']
        print('Docenti: ')
        for nome_docente in docenti.values():
            filename_docenti = nome_docente.replace(' ', '_')
            print(nome_docente)
            # print(check_lang)
            try:
                check_lang = textblob.TextBlob(nome_docente).detect_language()
                generate_audio_clip(text=nome_docente,
                                    filename=filename_docenti,
                                    rel_path=fp,
                                    lang=check_lang)
            except ValueError:
                generate_audio_clip(text=nome_docente,
                                    filename=filename_docenti,
                                    rel_path=fp)


def generate_corsi(override=False):
    """Generate the courses name audio cues.

    Keyword Arguments:
        override {bool} -- if True, overrides existing audio (default: {False})
    """
    fp = 'audio_library/corsi/'
    if override:
        delete_old(fp)
        corsi = catalog_names()['corsi']
        print('Corsi: ')
        for corso in corsi.values():
            nome_corso = corso['course_name']
            filename_corso = nome_corso.replace(' ', '_')
            print(nome_corso)
            # print(nome_corso, '-', check_lang)
            try:
                check_lang = textblob.TextBlob(nome_corso).detect_language()
                generate_audio_clip(
                    text=nome_corso, filename=filename_corso,
                    rel_path=fp, lang=check_lang)
            except ValueError:
                generate_audio_clip(
                    text=nome_corso, filename=filename_corso,
                    rel_path=fp)


def generate_other(override=False):
    """Generate other audio cues.

    Fonderie Sonore Podcast.  
    Materiale riservato agli studenti della scuola.  
    Podcast audio della, Corso, Docente, Del, Parte, Lezione  

    Keyword Arguments:
        override {bool} -- if True, overrides existing audio (default: {False})
    """
    fp = 'audio_library/other/'
    if override:
        delete_old(fp)
        mix_phrases = ['Fonderie Sonore Podcast', 'Podcast',
                       'Materiale riservato agli studenti della scuola',
                       'Podcast audio della:',
                       'Corso:', 'Docente:', 'Del:',
                       'Lezione', 'Parte:']
        print('Other: ')
        for phrase in mix_phrases:
            print(phrase)
            filename_phrase = phrase.replace(' ', '_')
            generate_audio_clip(
                text=phrase, filename=filename_phrase, rel_path=fp)


def generate_other_2(override=False):
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
    fp = 'audio_library/other_2/'
    # TODO need to generate till lezione 20
    if override:
        delete_old(fp)
        mix_phrases_2 = ['parte', 'Lezione']
        for phrase in mix_phrases_2:
            for i in range(1, 11):
                if phrase == 'parte':
                    text = f'{phrase} {i}ª'
                    filename_text = text.replace(' ', '_')
                    # generate_audio_clip()
                    print(text)
                    generate_audio_clip(
                        text=text, filename=filename_text, rel_path=fp)
                elif phrase == 'Lezione':
                    text = f'{i}ª {phrase}'
                    filename_text = text.replace(' ', '_')
                    generate_audio_clip(
                        text=text, filename=filename_text, rel_path=fp)
                    # print(i, phrase)
                    print(text)


def generate_numeri(override=False):
    """Generate ordinal numeric audio cues (1th, 2nd, 3rd).

    Keyword Arguments:
        override {bool} -- if True, overrides existing audio (default: {False})
    """
    fp = 'audio_library/numeri'
    if override:
        delete_old(fp)
        print('Numeri: ')
        for numero in range(1, 32):
            print(numero, 'ª')
            nome_numero = str(numero) + 'ª'
            file_name = nome_numero.zfill(2)
            generate_audio_clip(
                text=nome_numero, filename=file_name, rel_path=fp)


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
        fp = 'audio_library/data/giorni/'
        if override_all or override_giorni:
            delete_old(fp)
            print('Giorni: ')
            for giorno in range(1, 32):
                giorno_nome = str(giorno)
                file_name = f'{str(giorno).zfill(2)}'
                generate_audio_clip(
                    text=giorno_nome, filename=file_name,
                    rel_path=fp)
                print(giorno)

    def generate_mesi():
        fp = 'audio_library/data/mesi/'
        if override_all or override_mesi:
            delete_old(fp)
            mesi = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile',
                    'Maggio', 'Giugno', 'Luglio', 'Agosto',
                    'Settembre', 'Ottobre', 'Novembre', 'Dicembre']
            print('Mesi: ')
            n = 1
            for mese in mesi:
                # file_name = f'{str(n).zfill(2)}_{mese}'
                generate_audio_clip(
                    text=mese, filename=mese, rel_path=fp)
                n += 1
                print(mese)

    def generate_anni():
        fp = 'audio_library/data/anni/'
        if override_all or override_anni:
            delete_old(fp)
            print('Anni: ')
            for anno in range(2018, 2031):
                generate_audio_clip(text=anno, filename=anno, rel_path=fp)
                print(anno)

    generate_giorni()
    generate_mesi()
    generate_anni()


def generate_audio_clip(text, filename, rel_path, lang='it'):
    """Generate the audio cues.

    Arguments:
        text {str} - what is going to be spoke in the audio cue.
        file_name {str} - the name of the saved file.
        rel_path {str} - relative path of where to save the file.

    Keyword Arguments:
        lang {str} - the language for the audio(default: 'it')
    """
    name = str(text)
    speak = gtts.gTTS(text=name, lang=lang)
    speak.save(f'{rel_path}/{filename}.wav')


def delete_old(path):
    """Delete old audio files if overriding.

    Arguments:
        path {string} - - path like string for the directory in where to delete.
    """
    for item in os.listdir(path):
        file_path = os.path.join(path, item)
        os.remove(file_path)


if __name__ == '__main__':
    generate_docenti(override=True)
    generate_corsi(override=True)
    generate_numeri(override=True)
    generate_other(override=True)
    generate_other_2(override=True)
    generate_data(override_all=True, override_giorni=True,
                  override_mesi=True, override_anni=True)
