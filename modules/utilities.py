from discord.ext import commands, groups
from utils import check
import discord
import asyncio
import aiohttp
import mimetypes


class Utilities:
    def __init__(self, notus):
        self.notus = notus
        self.db = notus.db

    @property
    def settings(self):
        return self.db['settings']

    @commands.command()
    async def ping(self, ctx):
        """Pong."""
        await ctx.send("Pong.")

    @commands.group(name='set') # Needs testing.
    @check.instance_owner()
    async def utils_set(self, ctx):
        """Sets various stuff."""
        await self.notus.send_command_help(ctx)

    @utils_set.command(name="nickname", aliases=['nick'], usage="<name>")
    async def utils_set_nickname(self, ctx):
        """Sets bot nickname."""
        if not ctx.args:
            return await self.notus.send_command_help(ctx)

        try:
            if len(ctx.suffix) < 32:
                await ctx.msg.guild.me.edit(nick=ctx.suffix)
                await ctx.send("Beep Boop. Done.")
            else:
                await ctx.send(
                    "Character count is over 32!... Try with less characters.")
        except:
            await ctx.send("Error changing nickname, either "
                           "`Lacking Permissions` or `Something Blew Up`.")

    @utils_set.command(name="game", usage='[game]')
    async def utils_set_game(self, ctx):
        """Sets Bot's playing status."""
        await ctx.send("This command needs to be rewritten to adapt to Discord RPC.")

    @utils_set.command(name="status", usage='[status]')
    async def utils_set_status(self, ctx):
        """Sets bot presence."""
        if ctx.args:
            status = getattr(discord.Status, ctx.args[0], discord.Status.online)
        else:
            status = discord.Status.online

        await self.notus.change_presence(status=status)
        await ctx.send("Changed status!")

    @utils_set.command(name="owner", aliases=['owners'], usage='<owners: multiple>')
    async def utils_set_owner(self, ctx):
        """Sets other owners."""
        if not ctx.args:
            return await self.notus.send_command_help(ctx)

        owners = [await self.lookups.member_lookup(ctx, arg) for arg in ctx.args]
        owners = [str(x.id) for x in owners if isinstance(x, discord.Member) and str(x.id) not in
                  self.settings['owners']]
        self.settings['owners'].extend(owners)

        if len(owners) == 1:
            await ctx.send('Set other owner.')
        else:
            await ctx.send('Set other owners.')

    @utils_set.command(name="avatar")
    async def utils_set_avatar(self, ctx, *, url=None):
        """Changes the bots avatar"""
        if not url:
            if not ctx.msg.attachments:
                return await ctx.send("No avatar found! Provide an URL or attachment!")
            else:
                url = ctx.msg.attachments[0].url

        async with ctx.typing():
            ext = url.split(".")[-1]
            mime = mimetypes.types_map.get(ext)

            if mime is not None and not mime.startswith("image"):
                # None can still be an image
                return await ctx.send("URL or attachment is not an Image!")

            async with aiohttp.ClientSession() as s, s.get(url) as r:
                if 200 <= r.status < 300:
                    content = await r.read()
                else:
                    return await ctx.send("Invalid response code: {}".format(r.status_code))

            try:
                await self.notus.user.edit(avatar=content)
            except BaseException:  # I don't know the exact Exception type
                return await ctx.send("Avatar was too big or not an image!")

        await ctx.send("Successfully updated avatar!")

    @commands.group(name="blacklist") # also needs testing
    @check.instance_owner()
    async def blacklist_commands(self, ctx):
        """Prevents a user from using the bot globally."""
        await self.notus.send_command_help(ctx)

    @blacklist_commands.command(name="add")
    async def add_blacklist(self, ctx, *, user: discord.Member):
        """Adds a user to blacklist."""
        if str(user.id) not in self.settings['blacklist']:
            try:
                self.settings['blacklist'].append(str(user.id))
                await ctx.send("User blacklisted.")
            except:
                await ctx.send("An error occured.")
        else:
            await ctx.send("User already blacklisted.")

    @blacklist_commands.command(name="remove")
    async def remove_blacklist(self, ctx, *, user: discord.Member):
        """Removes a user from blacklist."""
        if str(user.id) not in self.settings['blacklist']:
            await ctx.send("User is not blacklisted.")
        else:
            self.settings['blacklist'].remove(str(user.id))
            await ctx.send("User removed from blacklist.")

# Needs Testing.

    @commands.command(aliases=['clean'])
    @check.instance_guild()
    async def cleanup(self, ctx):
        """Cleans up the bot's messages."""
        msgs = await ctx.msg.channel.history(limit=100).flatten()
        msgs = [msg for msg in msgs if msg.author.id == self.notus.user.id]

        if msgs and ctx.has_permission('manage_messages'):
            await ctx.msg.channel.delete_messages(msgs)
        elif msgs:
            for msg in msgs:
                await msg.delete()
        else:
            return

        msg = await ctx.send("Cleaned `{}`".format(len(msgs)))
        await asyncio.sleep(2.5)
        await msg.delete()

# Needs Testing.

def setup(notus):
    notus.add_cog(utilities())
