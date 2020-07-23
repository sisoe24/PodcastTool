import os
import sys
import json
import regex
import pathlib

from src.podcasttool import PodcastFile

dir_file = os.path.dirname(__file__)
file_path = ''.join([str(i) for i in pathlib.Path(dir_file).glob('*wav')])
test_file = file_path


def json_catalog():
    path = pathlib.Path(os.path.dirname(__file__)).parents
    for i in path:
        if i.parts[-1] == 'PodcastTool':
            json_path = i.joinpath('src', 'podcasttool', 'catalog_names.json')

    print(json_path)
    with open(json_path) as f:
        json_data = json.load(f)
    return json_data


file = PodcastFile(test_file)


def test_get_filename():
    podcast_name = os.path.basename(os.path.splitext(test_file)[0])
    assert file.name == podcast_name


def test_podcast_nome_docente():
    teachers = json_catalog()['docenti']
    assert file.teacher_name in teachers.values()
    assert isinstance(file.teacher_name, str)


def test_course_name():
    courses = json_catalog()['corsi']
    courses_name = [_['course_name'] for _ in courses.values()]
    assert file.course_name in courses_name
    assert isinstance(file.course_name, str)


# def test_registration_date():
#     print(file.registration_date)
#     valid_date = regex.match(
#         r'(\d\d)/([A-Za-z]+)/(\d{4})$', file.registration_date)
#     assert valid_date
#     assert valid_date.group(2) in file._convert_month_name().values()
#     assert isinstance(file.registration_date, str)


def test_lesson_number():
    valid_name = regex.match(r'\d{1,2}ª Lezione', file.lesson_number)
    assert valid_name
    assert isinstance(file.lesson_number, str)


def test_part_number():
    valid_name = regex.match(r'(P|p)arte \dª', file.part_number)
    assert valid_name
    assert isinstance(file.part_number, str)


if __name__ == '__main__':
    test_podcast_nome_docente()
