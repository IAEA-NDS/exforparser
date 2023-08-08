import setuptools

if __name__ == "__main__":
    setuptools.setup()

# from setuptools import setup, find_packages

# # print(find_packages())
# # --> return ['tabulated', 'parser', 'sql']

# def read_requirements(file):
#     with open(file) as f:
#         return f.read().splitlines()

# def read_file(file):
#    with open(file) as f:
#         return f.read()

# version = read_file("VERSION")
# requirements = read_requirements("requirements.txt")

# setup(
#     name="exforparser",
#     description="EXFOR Parser",
#     packages=find_packages(exclude=["test"]), 
#     py_modules=['exparser', 'tabulated'],
#     version=version,
#     author="Shin Okumura/IAEA-NDS",
#     author_email="s.okumura@iaea.org",
#     maintainer="IAEA-NDS",
#     maintainer_email="nds.contact-point@iaea.org",
#     license="GPL-2.0 license",
#     url="https://github.com/s.okumura@iaea.org/exforparser",
#     python_requires=">=3.8",
#     install_requires=requirements,
#     classifiers=[
#         "Programming Language :: Python :: 3",
#         "Operating System :: OS Independent",
#         "License :: OSI Approved :: GPL-2.0 license",
#     ],
# )
