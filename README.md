# Shlimpbot

A bot framework for the Atlantis Georgias (and maybe more), built using nextcord

## Setup and Run

Install Poetry  
`pip install poetry`

Set up environment (requires Python 3.9+)  
`poetry install`

Copy settings_example.json to a location of your choice and add your Discord bot token (default is settings.json in the
project root)

Run bot  
`poetry run shlimpbot`

If your settings file is not in the default location you can specify it as an env var
`SHLIMPBOT_SETTINGS=/path/to/settings.json poetry run shlimpbot`