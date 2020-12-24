import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="radxupsite-jsearcy1", # Replace with your own username
    version="0.0.1",
    author="Jake Searcy",
    author_email="jsearcy@uoregon.edu",
    description="A package to find optimial site locations for Covid-19 testing events",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jsearcy1/radxup_site",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
)
