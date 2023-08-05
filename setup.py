
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="manyworlds",
    version="0.0.1",
    author="Ingo Weiss",
    description="A more concise way to write BDD feature files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=["manyworlds"],
    package_dir={'Package':'manyworlds'},
    entry_points={ 'console_scripts': ['Package = manyworlds.__main__:main' ] },
    install_requires=[]
)
