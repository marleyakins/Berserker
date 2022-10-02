import sys
import discord
import json

from classes import Berserker, ConfigObject

def recursive_object_builder(obj: dict) -> ConfigObject:
    if isinstance(d, list):
        d = [recursive_object_builder(x) for x in d]

    if not isinstance(d, dict):
        return d

    obj = ConfigObject()

    for o in d:
        obj.__dict__[o] = recursive_object_builder(d[o])

    return obj

def load_config() -> ConfigObject:
    with open("config.toml", "r") as f:
        config = json.load(f)

    return recursive_object_builder(config)

def main() -> int:
    berserker = Berserker(intents=discord.Intents.all())

    config = load_config()
    for extension in config.extensions:
        berserker.load_extension(extension)

    berserker.run(config.token)
    return 0

if __name__ == "__main__":
    sys.exit(main())
