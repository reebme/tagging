#!/usr/bin/python3
# -*- coding: windows-1250 -*-

from os import walk
from os.path import join

import argparse
import mutagen

parser = argparse.ArgumentParser()
# ścieżka do folderów, które będą przeszukiwane
# TODO rozszerzenie opcji z jednego folderu na wiele folderów
parser.add_argument("path")
# lista tagow do wyswietlenia, wybór z listy dostępnych możliwości, jeśli
# argument występuje, musi towarzyszyć mu co najmniej jedna opcja z listy
# choices
parser.add_argument("-t", "--tags", nargs="+",
                    choices=["artist", "album", "title", "genre", "track"])
args = parser.parse_args()

ID3_INFO_FRAMES = {
    "album": "TALB",
    "title": "TIT2",
    "artist": "TPE1",
    "track": "TRCK",
    "genre": "TCON"
}

FILES_HERE = []
for dirpath, dirnames, filenames in walk(args.path):
    for short_name in filenames:
        FILES_HERE.append((dirpath, short_name))

REPLACEMENTS = {
    " ": "_",
    ".": "",
    "feat": "ft",
    "Feat": "ft"
}

for dirpath, short_name in FILES_HERE:
    # pełna nazwa
    full_name = join(dirpath, short_name)

    # rozszerzenie
    file_name, ext = short_name.rsplit(".", 1)

    # otwórz plik audio
    try:
        a_file = mutagen.File(full_name)
    except mutagen.mp3.HeaderNotFoundError as key_e:
        print("Brak nagłówka ID3")

    # plik MP3
    if ext == "mp3":
        print(full_name)
        tags = []
        if args.tags is not None:
            tags = args.tags
        else:
            tags = ID3_INFO_FRAMES.keys()
        for frame in tags:
            print(a_file.tags.getall(frame))
        print(a_file.info.pprint())


# audio_ext = set(['mp3', 'flac', 'm4a'])

# for dirpath, short_name in files_here:
    #   file_name, ext = short_name.rsplit(".", 1)
    #   if ext in audio_ext:
    #       try:
    #           audio_file = ID3(join(dirpath, short_name))
    #       except ID3NoHeaderError as e:
    #           print e
    #           continue
    #
    #       print "{:_^75}".format("")
    #       print "{:^75}".format(short_name)
    # #      for tag in ID3_info_frames:
    #           try:
    #               print "{:<10}{}".format(
    #                    ID3_info_frames[tag]+ ":", audio_file[tag])
    #           except KeyError:
    #               print "No key"

# TODO obsługa wyjątków
# TODO argument do walk z zewnątrz
# TODO wypisz pliki, dla których nie jest uzupełniony dany tag
# TODO zmiana nazw plików na podstawie tagów
