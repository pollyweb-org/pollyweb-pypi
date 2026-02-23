from setuptools import setup, find_packages

setup(
    name="pollyweb",
    version="0.1.1",
    description="A neutral, open, and global web protocol that allows any person or AI agent to chat with any business, place, or thing.",
    author="jorgemf",
    license="Apache-2.0",
    url="https://www.pollyweb.org",
    project_urls={
        "Website": "https://www.pollyweb.org",
        "Logo": "https://www.pollyweb.org/images/pollyweb-logo.png",
    },
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.7',
)
