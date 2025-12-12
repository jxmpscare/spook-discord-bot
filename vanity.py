# open sourced, made by @.j_e_t on discord // jet

import discord
from discord.ext import commands, tasks
from discord.ext.commands import CooldownMapping, BucketType
import json
import os

DATA_FILE = "vanity_storage_unit.json"

class Vanity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.user)
        self.load_data()
        self.checks.start()

    def load_vanity_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def store_vanity_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    @commands.group()
    async def vanity(self, ctx):
        bucket = self._cd.get_bucket(ctx.message)
        retry = bucket.update_rate_limit()
        
        if retry:
            embed = discord.Embed(
                description=f"{cooldown} You're running commands too fast, please wait ```{retry:.1f}s``` then try again." 
            )
            await ctx.send(embed=embed)
            return

        # spooks help menu lol
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title=f"{folder} Command: vanity",
                description="> give people a role for representing your server."
            )
            embed.add_field(name="📃 Aliases", value="`van`, `rep`", inline=True)
            embed.add_field(name=f"{perms} Permissions", value="Administrator", inline=True)
            embed.add_field(name=f"{premium} Premium", value="No", inline=True)
            embed.add_field(name="Usage", value="```Syntax: ;vanity <reward> <role>\nSyntax 2: ;vanity <set> <vanity>\nExample 1: ;vanity reward @coolpeople\nExample 2: ;vanity set sexygirls```", inline=False)
            embed.set_footer(text="<> = required / [] = optional / Module: Vanity")
            embed.set_author(name="spook help", icon_url="https://i.postimg.cc/BbSpRS77/ww.png")
            await ctx.send(embed=embed)

    # reward role func
    @vanity.command()
    @commands.has_permissions(administrator=True)
    async def reward(self, ctx, role: discord.Role):
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.data:
            self.data[guild_id] = {}
        
        self.data[guild_id]["reward_role"] = role.id
        self.save_data()
        
        embed = discord.Embed(
            description=f"{approve} {ctx.author.mention}: Reward role set to {role.mention}"
        )
        await ctx.send(embed=embed)

    # set function
    @vanity.command()
    @commands.has_permissions(administrator=True)
    async def set(self, ctx, vanity_name: str):
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.data:
            self.data[guild_id] = {}
        
        self.data[guild_id]["vanity_name"] = vanity_name.lower()
        self.save_data()
        
        embed = discord.Embed(
            description=f"{approve} Vanity name set to `{vanity_name}`"
        )
        await ctx.send(embed=embed)

    # constant checking for repping
    @tasks.loop(seconds=0.5)
    async def checks(self):
        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            
            if guild_id not in self.data:
                continue
            
            vanity_data = self.data[guild_id]
            if "vanity_name" not in vanity_data or "reward_role" not in vanity_data:
                continue
            
            vanity_name = vanity_data["vanity_name"]
            reward_role_id = vanity_data["reward_role"]
            reward_role = guild.get_role(reward_role_id)
            
            if not reward_role:
                continue
            
            for member in guild.members:
                if member.bot:
                    continue
                
                # does the user have /{vanity} in their name
                has_vanity = False
                if member.activity:
                    activity_text = str(member.activity).lower()
                    if vanity_name in activity_text:
                        has_vanity = True
                
                # this will take the role or give, depends on status
                if has_vanity and reward_role not in member.roles:
                    try:
                        await member.add_roles(reward_role)

                
                elif not has_vanity and reward_role in member.roles:
                    try:
                        await member.remove_roles(reward_role)

    # this waits for the bot to start                 
    @checks.before_loop
    async def before(self):
        await self.bot.wait_until_ready()

    # when the bot goes off
    def cog_unload(self):
        self.checks.cancel()

async def setup(bot):
    await bot.add_cog(Vanity(bot))
