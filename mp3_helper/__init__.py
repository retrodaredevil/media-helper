from pathlib import Path

import eyed3


def real_main():
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


def main():
    try:
        real_main()
    except KeyboardInterrupt:
        print("\nExiting")


if __name__ == '__main__':
    main()
