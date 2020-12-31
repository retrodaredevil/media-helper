from setuptools import setup, find_packages

setup(
    name="media_helper",
    version="0.1",
    packages=find_packages(),
    author="retrodaredevil",
    author_email="retrodaredevil@gmail.com",
    description="Scripts to help with managing media names and metadata",
    url="https://github.com/retrodaredevil/mp3-helper",
    entry_points={"console_scripts": ["mp3-helper = media_helper:do_mp3_helper",
                                      "add-leading-zeros = media_helper:do_add_leading_zeros",
                                      "tv-rename = media_helper:do_tv_rename"]},
    install_requires=["eyed3"]
)
