import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="monday-outlook-integration",
    version="0.1",
    author="John Meehan",
    author_email="jmeehan@amuneal.com",
    description="A tool to import web requests into monday.com automatically",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meehanjohn/monday-email-integration",
    packages=setuptools.find_packages()
)
