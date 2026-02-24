from setuptools import setup, find_packages

setup(
    name="pollyweb",
    version="0.1.10",
    description="A neutral, open, and global web protocol that allows any person or AI agent to chat with any business, place, or thing.",
    author="jorgemf",
    author_email="pollyweb@pollycore.net",
    license="Apache-2.0",
    url="https://www.pollyweb.org",
    project_urls={
        "Website": "https://www.pollyweb.org",
        "Logo": "https://www.pollyweb.org/images/pollyweb-logo.png",
    },
    packages=find_packages(),
    install_requires=["cryptography>=41.0.0", "websocket-client>=1.6.0"],
    entry_points={
        "console_scripts": [
            # helper scripts for the demos
            "pollyweb-keys=pollyweb.demo.keys:main",
            "pollyweb-setup=pollyweb.demo.setup:main",
            "pollyweb-emulate=pollyweb.demo.emulate:main",
        ],
    },
    python_requires='>=3.7',
)
