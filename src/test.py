"""Testing how to modify PodcastGenerator class."""
from generate_podcast_copy import PodcastFile, PodcastGenerator


PATH = "other/Scrivania/Podcast/EMP/SCE4/"
FILES = [f"{PATH}SCE4_20190228_E_Cosimi_Lezione_8_parte_1.wav",
         f"{PATH}SCE4_20190228_E_Cosimi_Lezione_8_parte_2.wav"]
RAW_PODCAST = FILES[0]

PODCAST = PodcastFile(RAW_PODCAST)
print(PODCAST.generate_podcast())
