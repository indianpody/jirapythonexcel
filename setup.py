import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jirapythonexcel",
    version="1.2.0",
    author="Indian Pody",
    author_email="prashant.poddar@gmail.com",
    description="Extracting jira information into excel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/indianpody/jirapythonexcel",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
