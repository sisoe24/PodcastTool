import os
import sys
import json
import regex
import pathlib

import pytest

from src.tools.podcasttools import PodcastFile


@pytest.fixture(autouse=True)
def initiate_podcast():
    dir_file = os.path.dirname(__file__)
    test_file = pathlib.Path(os.path.abspath(__file__)).parent / \
        'src/resources/samples/ALP/ABLO/ABLO_20210516_J_Lattanzio_Lezione_0_parte_0.wav'
    yield test_file


# @pytest.fixture(test_file, autouse=True)
# def create_podcast_class():
#     file = PodcastFile(test_file)
#     yield file


def json_catalog():
    path = pathlib.Path(os.path.dirname(__file__)).parents
    for i in path:
        if i.parts[-1] == 'PodcastTool':
            json_path = i.joinpath('src', 'podcasttool', 'catalog_names.json')

    print(json_path)
    with open(json_path) as f:
        json_data = json.load(f)
    return json_data


# file = PodcastFile(test_file)

# @pytest.mark
# @pytest.mark.parametrize('test_file', ['SEC6_20201212_E_Cosimi_Lezione_1_parte_3.wav'])
# @pytest.mark.parametrize('file', [PodcastFile('SEC6_20201212_E_Cosimi_Lezione_1_parte_3.wav')])
def test_get_filename(test_file, file):
    print("➡ file :", file)
    print("➡ test_file :", test_file)

    podcast_name = os.path.basename(os.path.splitext(test_file)[0])
    print("➡ podcast_name :", podcast_name)

    assert file.name == podcast_name


# def test_podcast_nome_docente():
#     teachers = json_catalog()['docenti']
#     assert file.teacher_name in teachers.values()
#     assert isinstance(file.teacher_name, str)


# def test_course_name():
#     courses = json_catalog()['corsi']
#     courses_name = [_['course_name'] for _ in courses.values()]
#     assert file.course_name in courses_name
#     assert isinstance(file.course_name, str)


# # def test_registration_date():
# #     print(file.registration_date)
# #     valid_date = regex.match(
# #         r'(\d\d)/([A-Za-z]+)/(\d{4})$', file.registration_date)
# #     assert valid_date
# #     assert valid_date.group(2) in file._convert_month_name().values()
# #     assert isinstance(file.registration_date, str)


# def test_lesson_number():
#     valid_name = regex.match(r'\d{1,2}ª Lezione', file.lesson_number)
#     assert valid_name
#     assert isinstance(file.lesson_number, str)


# def test_part_number():
#     valid_name = regex.match(r'(P|p)arte \dª', file.part_number)
#     assert valid_name
#     assert isinstance(file.part_number, str)


if __name__ == '__main__':
    test_podcast_nome_docente()
