import setuptools

setuptools.setup(
    name="discord-bot",
    packages=["bot"],
    install_requires=[
        "discord.py==1.7.3",
        "python-dotenv==0.18.0",
        "requests==2.25",
    ]
)