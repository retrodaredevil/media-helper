from argparse import ArgumentParser
from pathlib import Path

import eyed3
import sys

from typing import Callable, List, Optional, Iterator


def __do_func(func: Callable[[List[str]], int]) -> None:
    try:
        sys.exit(func(sys.argv[1:]))
    except KeyboardInterrupt:
        print("\nExiting")


def mp3_helper_main(args: List[str]) -> int:
    print("Starting")
    path = Path(".").resolve()
    album_name = path.name
    artist_name = Path(path, "..").resolve().name
    for file in path.iterdir():
        if file.is_file() and file.name.endswith(".mp3"):
            first_part = file.name.split(" ")[0]
            number = None
            try:
                number = int(first_part)
            except ValueError:
                pass

            audio_file = eyed3.load(file)
            # audio_file.tag.artist = ""
            audio_file.tag.album = album_name
            audio_file.tag.album_artist = artist_name
            # audio_file.tag.title = ""
            if number is not None:
                audio_file.tag.track_num = number

            audio_file.tag.save()
    print("Done")
    return 0


def do_mp3_helper():
    __do_func(mp3_helper_main)


def add_leading_zeros_main(args: List[str]) -> int:
    for file in Path(".").iterdir():
        if not file.is_dir():
            name = file.name
            split = name.split(" ")
            numeric_indexes = [i for i, part in enumerate(split) if part.isnumeric()]
            for index in numeric_indexes:
                split[index] = "{:02d}".format(int(split[index]))
            new_name = " ".join(split)
            if new_name != name:
                print("Going to rename {} to {}".format(name, new_name))
                file.rename(Path(file.parent, new_name))
    return 0


def do_add_leading_zeros():
    __do_func(add_leading_zeros_main)


def get_file_iter(files: Optional[List[str]], recursive: bool) -> Iterator[Path]:
    if not files and not recursive:
        yield from Path(".").iterdir()
    if not files:
        files = ["."]  # we can do this since recursive is true

    def generator_function(my_files):
        for file in my_files:
            path = Path(file)
            if path.is_dir():
                if recursive:
                    yield from generator_function(path.iterdir())
            else:
                yield path

    yield from generator_function(files)


def tv_rename_main(args: List[str]) -> int:
    parser = ArgumentParser()
    parser.add_argument("files", type=str, nargs="*", help="The files to rename", default=None)
    parser.add_argument("--season", type=int, help="Override the season", default=None)
    parser.add_argument("-r", action="store_true")
    parser.add_argument("--episode-start", type=int, default=1, help="Define the starting episode number")
    parser.add_argument("--allow-overwrite", action="store_true",
                        help="Use if you want to overwrite files when there's a conflicting file name")
    parser.add_argument("--test", action="store_true",
                        help="Use to see what files will be renamed to before actually doing it")

    def find_number(indicators: List[str], text: str) -> Optional[int]:
        for indicator in indicators:
            sub_text = text
            while True:
                index = sub_text.find(indicator)
                if index < 0:
                    break

                start_index = index + len(indicator)
                sub = sub_text[start_index:] + "a"  # add random character to prevent index error in code below
                sub_text = sub_text[index + 1:]  # the new sub_text for next iteration
                while sub.startswith(" "):
                    sub = sub[1:]
                number_text = sub[0]
                while True:
                    try_index = len(number_text)
                    if try_index < len(sub) and sub[try_index].isdigit():
                        number_text += sub[try_index]
                    else:
                        break
                try:
                    return int(number_text)
                except ValueError:
                    pass
        return None
    args = parser.parse_args()
    all_season = args.season
    test = args.test
    allow_overwrite = args.allow_overwrite
    episode_start = args.episode_start
    for file in get_file_iter(args.files, args.r):
        if not file.is_dir():
            name = file.name
            file_extension = name.split(".")[-1]
            if file_extension == name:
                partial_name = name
            else:
                partial_name = name[0:-len(file_extension) - 1]
            if all_season is None:
                season = find_number(["season", "s"], partial_name.lower())
                if season is None:
                    print("Couldn't find season in file name: " + name)
                    return 1
            else:
                season = all_season

            episode = find_number(["episode", "e"], partial_name.lower())
            if episode is None:
                print("Couldn't find episode in file name: " + name)
                return 1
            episode += episode_start - 1
            new_name = "S{:02d}E{:02d}.{}".format(season, episode, file_extension)
            if test:
                print("{} will be renamed to {}".format(name, new_name))
            else:
                new_file = Path(file.parent, new_name)
                if new_file != file:  # if it's the same file, don't do anything
                    if new_file.exists() and not allow_overwrite:
                        print("new file exists! new name: " + new_name + " old name: " + name)
                        return 1
                    file.rename(new_file)

    return 0


def do_tv_rename():
    __do_func(tv_rename_main)
