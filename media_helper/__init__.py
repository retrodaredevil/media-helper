from argparse import ArgumentParser
from itertools import count
from pathlib import Path

import eyed3
import sys

from typing import Callable, List, Optional, Iterator, Tuple

SEPARATOR = "–"  # Note that this character is not a dash
SEPARATORS = ["–", "-"]


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


def trim(text: str) -> str:
    text = text.strip()

    while any(text.startswith(separator) for separator in SEPARATORS):
        text = text[1:]

    while any(text.endswith(separator) for separator in SEPARATORS):
        text = text[:-1]

    return text.strip()


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
    parser.add_argument("--upper", action="store_true", help="If set, uses S00E00.ext format instead of s00e00.ext")
    parser.add_argument("--lower", action="store_true",
                        help="If set, uses s00e00.ext format instead of S00E00.ext. Has affect if --jelly is set")
    parser.add_argument("--jelly", action="store_true", help="Makes output match Jellyfin recommendations")
    parser.add_argument("--auto-show-name", action="store_true", help="Tries to guess show name")
    parser.add_argument("--auto-episode-name", action="store_true", help="Tries to guess episode name")
    parser.add_argument("--auto-episode-ignore-after", type=str, default=None)
    parser.add_argument("--show-name", type=str, default=None)

    def find_number(indicators: List[str], text: str) -> Optional[Tuple[int, int, int]]:
        for indicator in indicators:
            sub_text = text

            while True:
                indicator_start_index = sub_text.find(indicator)
                if indicator_start_index < 0:
                    break

                shaved_length = len(text) - len(sub_text)
                number_start_index = indicator_start_index + len(indicator)
                sub = sub_text[number_start_index:] + "a"  # add random character to prevent index error in code below
                sub_text = sub_text[indicator_start_index + 1:]  # the new sub_text for next iteration
                counter = 0
                while sub.startswith(" "):
                    sub = sub[1:]
                    counter += 1
                number_text = sub[0]
                while True:
                    try_index = len(number_text)
                    if try_index < len(sub) and sub[try_index].isdigit():
                        number_text += sub[try_index]
                    else:
                        break
                counter += len(number_text)
                try:
                    return int(number_text), shaved_length + indicator_start_index, shaved_length + number_start_index + counter
                except ValueError:
                    pass
        return None
    args = parser.parse_args()
    all_season = args.season
    test = args.test
    allow_overwrite = args.allow_overwrite
    episode_start = args.episode_start
    upper = args.upper
    jelly = args.jelly
    if jelly:
        upper = True
    if args.lower:
        if args.upper:
            print("--lower and --upper cannot be set at same time.")
            return 1
        upper = False
    season_letter, episode_letter = ("S", "E") if upper else ("s", "e")
    for file in get_file_iter(args.files, args.r):
        if not file.is_dir():
            name = file.name
            file_extension = name.split(".")[-1]
            if file_extension == name:
                partial_name = name
            else:
                partial_name = name[0:-len(file_extension) - 1]

            season_tuple = find_number(["season", "s"], partial_name.lower())
            season, season_start_index, season_end_index = None, None, None
            if season_tuple is not None:
                season, season_start_index, season_end_index = season_tuple
            if all_season is None:
                if season_tuple is None:
                    print("Couldn't find season in file name: " + name)
                    return 1
                assert season is not None
                assert season_start_index is not None
                assert season_end_index is not None
            else:
                season = all_season

            episode_tuple = find_number(["episode", "e"], partial_name.lower())
            if episode_tuple is None:
                print("Couldn't find episode in file name: " + name)
                return 1
            episode, episode_start_index, episode_end_index = episode_tuple
            episode += episode_start - 1
            prefix = ""
            suffix = ""
            if jelly:
                prefix = "Episode "
            else:
                if args.auto_episode_name:
                    last = episode_end_index if season_end_index is None else max(episode_end_index, season_end_index)
                    ending = partial_name[last + 1:]
                    if args.auto_episode_ignore_after:
                        ending = ending.split(args.auto_episode_ignore_after)[0]
                    if ending:
                        suffix = " {} {}".format(SEPARATOR, trim(ending))

                if args.show_name is not None:
                    prefix = "{} {} ".format(args.show_name, SEPARATOR)
                elif args.auto_show_name:
                    index = episode_start_index if season_start_index is None else min(season_start_index, episode_start_index)
                    starting = partial_name[0:index]
                    if starting:
                        prefix = "{} {} ".format(trim(starting), SEPARATOR)
            new_name = "{}{}{:02d}{}{:02d}{}.{}"
            new_name = new_name.format(prefix, season_letter, season, episode_letter, episode, suffix, file_extension)
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
