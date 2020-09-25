import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tf2-stats-AlexHodgson", # Replace with your own username
    version="Alpha 1.2.1",
    author="Alex Hodgson",
    author_email="alexander.whodgson@gmail.com",
    description="ETF2L Stats for display and analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlexHodgson/tf2-stats",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Windows",
    ],
    python_requires='>=3.6',
)