from __future__ import annotations

import discord
from discord.ext import commands

import shelve
import json
import os

def func_check(check: bool, function: Callable, *args, **kwargs):
    """Runs a function if a given check is valid.
    Parameters:
       check: bool - What is checked before the function is run
       function: Callable - The function run if the check is True
    """
    if check:
        function(args, kwargs)


def add_guild_to_db(guild_id: str, bot):
    """Adds a guild to the guilds database
    Parameters:
       guild_id: str - The guild you would like to check
       bot: Berserker - The bot itself
    """
    bot.db['guilds'][str(guild.id)] = {}
    bot.db['guilds'][str(guild.id)]['cases'] = {}
    bot.db['guilds'][str(guild.id)]['case_num'] = 0

    bot.dump("guilds")
    return


def database_check(guild_id: str, bot):
    """Checks if a guild is registered for the guild's database.
    Parameters:
       guild_id: str - The guild you would like to check
       bot: Berserker - The bot itself
    """
    func_check(
        str(guild.id) not in bot.db["guilds"], add_guild_to_db, guild_id, bot
    )

    bot.dump("guilds")

def recursive_object_builder(d):
    """Returns a dictionary as an object class.
    Parameters:
      d: dict - The dictionary whose keys and values will become an object.
    """
    if isinstance(d, list):
        d = [recursive_object_builder(x) for x in d]

    if not isinstance(d, dict):
        return d

    class Obj:
        pass

    obj = Obj()

    for o in d:
        obj.__dict__[o] = recursive_object_builder(d[o])

    return obj

class Berserker(commands.AutoShardedBot):
    """Build and run base Berserker class.
    Child of `discord.ext.commands.AutoShardedBot`
    """

    def __init__(self, *args, **kwargs):
        self.__config_state = False
        self.__config = None
        
        super().__init__(
            command_prefix=self.__get_prefix,
            intents=discord.Intents.all(),
            self_bot=True, # ignore output that is not from interactions.
            strip_after_prefix=True,
            case_insensitive=True,
            chunk_guilds_at_startup=False,
            activity=discord.Activity(
                type=discord.ActivityType.listening, name=f"{self.config.DEFAULT_PREFIX}help"
            ),
            *args,
            **kwargs
        )

        self.__default_prefix = self.config.DEFAULT_PREFIX

        #     self.db = {
        #       "prefixes": shelve.open(self.config.PREFIX_TABLE_PATH),
        #       "guilds": shelve.open(self.config.GUILD_TABLE_PATH),
        #       "users": shelve.open(self.config.USER_TABLE_PATH)
        #     }

        # makes sure that the database has all necessary attributes to run the bot properly
        #     __build_database(self.db)

        self.loaded = {
            "prefixes": False,
            "guilds": False,
            "users": False,
        }

        self.__db = {} # a dictionary to load databases from given that they are loaded.

        for ext in self.config.EXTENSIONS:
            self.load_extension(ext)

    @property
    def db(self):
        """Returns a dictionary of open shelves."""
        # return {
        #     "prefixes": shelve.open(self.config.PREFIX_TABLE_PATH),
        #     "guilds": shelve.open(self.config.GUILD_TABLE_PATH),
        #     "users": shelve.open(self.config.USER_TABLE_PATH),
        # }

        _return = {}

        if self.loaded["prefixes"]:

            with open(self.config.PREFIX_TABLE_PATH, "r+") as f:
                _dict = json.load(f)
                _return["prefixes"] = _dict
                self.loaded["prefixes"] = True
                self.__db["prefixes"] = _dict

        else:
            _return["prefixes"] = self.__db["prefixes"]

        if self.loaded["guilds"]:

            with open(self.config.GUILD_TABLE_PATH, "r+") as f:
               _dict = json.load(f)
               _return["guilds"] = _dict
               self.loaded["guilds"] = True
               self.__db["guilds"] = _dict

        else:
            _return["guilds"] = self.__db["guilds"]

        if self.loaded["users"]:

            with open(self.config.USER_TABLE_PATH, "r+") as f:
               _dict = json.load(f)
               _return["users"] = _dict
               self.loaded["users"] = True
               self.__db["users"] = _dict

        else:
            _return["users"] = self.__db["users"]

        return _return

    def dump(self, db: str):
        """Dumps a given database table from the Berserker.db property.
        
        Parameters:
            db: str - The database to be dumped.
        """
        if db == "prefixes":
            with open(self.config.PREFIX_TABLE_PATH, "w+") as f:
                json.dump(self.db["prefixes"], f)
                self.loaded["prefixes"] = False
                del self.__db["prefixes"]

        elif db == "guilds":
            with open(self.config.GUILD_TABLE_PATH, "w+") as f:
                json.dump(self.db["guilds"], f)
                self.loaded["guilds"] = False
                del self.__db["guilds"]

        elif db == "users":
            with open(self.config.USER_TABLE_PATH, "w+") as f:
                json.dump(self.db["users"], f)
                self.loaded["users"] = False
                del self.__db["users"]

    @property
    def config(self):
        """Build and return config.json as an object."""
        # returns config object that has already been loaded if it has been loaded in the past
        if self.__config_state:
            return self.__config
        with open("config.toml", 'r') as f:
            config_obj = recursive_object_builder(json.load(f))

        self.__config_state = True
        self.__config = config_obj
        return config_obj

    def __get_prefix(self, message: discord.Message):
        """Returns a guild's set prefix or the default prefix.
        Parameters:
           message: discord.Message - The context message for the prefix.
        """
        return self.__default_prefix

    async def process_commands(self, message: Message) -> None:
        """|coro|
        This function processes the commands that have been registered
        to the bot and other groups. Without this coroutine, none of the
        commands will be triggered.
        By default, this coroutine is called inside the :func:`.on_message`
        event. If you choose to override the :func:`.on_message` event, then
        you should invoke this coroutine as well.
        This is built using other low level tools, and is equivalent to a
        call to :meth:`~.Bot.get_context` followed by a call to :meth:`~.Bot.invoke`.
        This also checks if the message's author is a bot and doesn't
        call :meth:`~.Bot.get_context` or :meth:`~.Bot.invoke` if so.
        Parameters
        -----------
        message: :class:`discord.Message`
            The message to process commands for.
        """
        if message.author.bot:
            return

        ctx = await self.get_context(message, discord.Context)
        await self.invoke(ctx)

    async def on_message(self, message: discord.Message):
        """The general on_message event listener. When overridden, commands will not register unless this function, or any equivalent is likewise called.
        Parameters:
           message: discord.Message - The message registered by the listener.
        """
        database_check(str(message.guild.id), self)
        for word in self.db["guilds"][str(message.guild.id)]['banned_words']:
            if word in message.content.lower():
                await message.delete()

                await message.channel.send(
                    embed = discord.Embed(
                        description="🚫  Message deleted for banned words. 🚫",
                        color=discord.Colour.red(),
                    ),
                    delete_after = 3
                )

                await message.author.send(
                    embed = discord.Embed(
                        title="🚫  Such language is not permitted. 🚫",
                        description=message.content,
                        color=discord.Colour.red(),
                    ),
                )

                # await self.raise_banned_word()

        await self.process_commands(message)
