import asyncio
from discord.ext import commands

class Room(object):
    def __init__(self, id, author):
        self.id = id
        self.author = author
        self.users = []
        self.users.append(author)

    def begin_deletion(self, channel):
        try:
            await self.bot.wait_for('voice_state_update', check=lambda m, b, c: m == self.author and c == self.id, timeout=5*60) # 5 minutes
        except asyncio.TimeoutError:
            await channel.delete()

        return

    def add_user(self, user):
        self.users.append(user)

    def remove_user(self, user):
        if user == self.author:
            channel = self.bot.get_channel(self.id)
            self.begin_deletion(channel)

        self.users.remove(user)

class Listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rooms = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        if before.channel is not None and after.channel is not None and before.channel.id == after.channel.id:
            return
        elif before.channel is not None and after.channel is None:
            await self.on_voice_leave(member, before.channel)

        elif before.channel is None and after.channel is not None:
            await self.on_voice_join(member, after.channel)

        else:
            await self.on_voice_move(member, before.channel, after.channel)

    async def on_voice_join(self, member, channel):
        if channel.id in self.rooms:
            self.rooms[channel.id].add_user(member)
        else:
            self.rooms[channel.id] = Room(channel.id, member)

    async def on_voice_leave(self, member, channel):
        if channel.id in self.rooms:
            self.rooms[channel.id].remove_user(member)

    async def on_voice_move(self, member, before, after):
        if before.id in self.rooms:
            self.rooms[before.id].remove_user(member)

        if after.id in self.rooms:
            self.rooms[after.id].add_user(member)
        else:
            self.rooms[after.id] = Room(after.id, member)
