from setuptools import setup, find_packages

setup(
    name="mp3_helper",
    version="0.1",
    packages=find_packages(),
    author="retrodaredevil",
    author_email="retrodaredevil@gmail.com",
    description="Simple mp3 helper script",
    url="https://github.com/retrodaredevil/mp3-helper",
    entry_points={"console_scripts": ["mp3-helper = mp3_helper:main"]}
)
