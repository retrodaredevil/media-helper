# Media Helper
A collection of scripts to help with metadata and file renaming

## Quick installation
```shell script
sudo python3 -m pip install git+git://github.com/retrodaredevil/media-helper.git
```

## Using `tv-rename`
Renames files in a directory to match the S00E00.ext format

Usage:
```shell
tv-rename --season 1 --episode-start 1 --test *  # Use of * is optional.
```

## Using `mp3-helper`
Add metadata to mp3 files if you have the file directory structure `{artist}/{album}/{00} - Song.mp3`

Usage:
```shell
cd <some working directory>
mp3-helper
```

## Using `add-leading-zeros`
Adds leading zeros to numbers in file names

Usage:
```shell
add-leading-zeros
```

### More useful stuff
Also, this command is useful for removing the "Season 01" part: 
```
for filename in *.mp4; do [ -f "$filename" ] || continue; mv "$filename" "${filename//Season 01 /}"; done
```
