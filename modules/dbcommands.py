# Base Modules for Bot
import discord
import asyncio
import aiomysql
from discord.ext import commands
import traceback

# Misc. Modules
import datetime
import config as cfg


class DBCommandsCog:
    def __init__(self, bot):
        self.bot = bot

    # Error handling
    '''
	async def on_command_error(self, ctx, error):

		# This prevents any commands with local handlers being handled here in on_command_error.
		if hasattr(ctx.command, 'on_error'):
			return
		embed = discord.Embed(title=f"**EXCEPTION** \U0000274c",
		                      colour=discord.Colour(0xf44b42))
		embed.set_footer(text="PGServerManager | TwiSt#2791")
		embed.add_field(name="There was the following exception!",
		                value=f"```{error}```")
		await ctx.send(embed=embed)
		channel = self.bot.get_channel(491104127573557268)
		await channel.send(embed=embed)
	'''

    # --------------ID Checks--------------
    async def check_id(self, user: discord.Member):
        # Check if ID exists
        await self.bot.discur.execute('SELECT PlayerUID FROM users WHERE DiscordUser = %s;', (str(user),))
        result = await asyncio.gather(self.bot.discur.fetchone())
        # Check if anything was returned
        if result[0] == None:
            return False
        else:
            return True

    async def get_steamid(self, user: discord.Member):
        await self.bot.discur.execute('SELECT PlayerUID from users WHERE DiscordUser = %s;', (str(user),))
        result = await asyncio.gather(self.bot.discur.fetchone())
        realsteamid = result[0]
        realsteamid = realsteamid.get('PlayerUID')
        return realsteamid

    async def validsteamidcheck(self, ctx, steamid):
        if (steamid[:7] == "7656119" and len(steamid) == 17):
            return True
        else:
            return False

    # --------------Logging--------------
    async def amountlog(self, ctx, amount, user, admin, type):
        embed = discord.Embed(
            title=f"{type} Log \U00002705", colour=discord.Colour(0xFFA500))
        embed.set_footer(text="PGServerManager | TwiSt#2791")
        embed.add_field(
            name="Data:", value=f"{admin} gave {user.mention} {amount} {type}!")

        channel = self.bot.get_channel(488893718125084687)
        await channel.send(embed=embed)

    # --------------Commands--------------
    @commands.command()
    @commands.has_any_role("Owner", "Manager", "Developer", "Head Admin", "Super Admin")
    async def coins(self, ctx, player: discord.Member, amount: int):
        '''
        Changes a player's BankCoins in the Database
        '''
        # Open Connection
        dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
        dzcur = await dzconn.cursor(aiomysql.DictCursor)

        # Checks to see if user is registered
        if await DBCommandsCog.check_id(self, player):
            steamid = await DBCommandsCog.get_steamid(self, player)

            embed = discord.Embed(
                title=f"ReactToConfirm \U0001f4b1", colour=discord.Colour(0xFFA500))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(name="Type:", value=f"`Coins`")
            embed.add_field(name="Amount:", value=f"`{amount}`")
            embed.add_field(name="STEAM64ID:", value=f"`{steamid}`")
            message = await ctx.send(embed=embed)
            await message.add_reaction("\U0001f44d")
            await message.add_reaction("\U0001f44e")

            def reactioncheck(reaction, user):
                validreactions = ["\U0001f44d", "\U0001f44e"]
                return user.id == ctx.author.id and reaction.emoji in validreactions
            reaction, user = await self.bot.wait_for('reaction_add', check=reactioncheck)
            # Check if thumbs up
            if reaction.emoji != "\U0001f44d":
                await ctx.send("Command cancelled")
                return

            # Get starting value
            await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
            original = await asyncio.gather(dzcur.fetchone())

            # Perform the query
            await dzcur.execute('UPDATE player_data SET BankCoins = BankCoins + %s WHERE PlayerUID = %s;', (amount, steamid))

            # Check if it actually changed
            await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
            new = await asyncio.gather(dzcur.fetchone())
            if(new == original):
                await ctx.send("An error has occured! Nothing has been changed. Please fix your syntax")
            else:
                embed = discord.Embed(
                    title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Data:", value=f"{player.mention} has received **{amount} Coins to Bank**!")
                embed.add_field(
                    name="Original:", value=f"{player.mention} had **{original[0]['BankCoins']} Coins in Bank**!")
                embed.add_field(
                    name="New:", value=f"{player.mention} now has **{new[0]['BankCoins']} Coins in Bank**!")
                await ctx.send(embed=embed)
                admin = ctx.message.author
                await DBCommandsCog.amountlog(self, ctx, amount, player, admin, "Coins to Bank")
        else:
            await ctx.send(f"The DiscordUser: {player.mention} is not registered.")

        # Close Connection
        dzconn.close()

    @commands.command()
    @commands.has_any_role("Owner", "Manager", "Developer", "Head Admin", "Super Admin")
    async def xp(self, ctx, player: discord.Member, amount: int):
        # Open Connection
        dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
        dzcur = await dzconn.cursor(aiomysql.DictCursor)

        if await DBCommandsCog.check_id(self, player):
            steamid = await DBCommandsCog.get_steamid(self, player)

            embed = discord.Embed(
                title=f"ReactToConfirm \U0001f4b1", colour=discord.Colour(0xFFA500))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(name="Type:", value=f"`XP`")
            embed.add_field(name="Amount:", value=f"`{amount}`")
            embed.add_field(name="STEAM64ID:", value=f"`{steamid}`")
            message = await ctx.send(embed=embed)
            await message.add_reaction("\U0001f44d")
            await message.add_reaction("\U0001f44e")

            def reactioncheck(reaction, user):
                validreactions = ["\U0001f44d", "\U0001f44e"]
                return user.id == ctx.author.id and reaction.emoji in validreactions
            reaction, user = await self.bot.wait_for('reaction_add', check=reactioncheck)
            # Check if thumbs up
            if reaction.emoji != "\U0001f44d":
                await ctx.send("Command cancelled")
                return

            # Get starting value
            await dzcur.execute('SELECT XP FROM xpsystem WHERE PlayerUID = %s;', (steamid,))
            original = await asyncio.gather(dzcur.fetchone())

            await dzcur.execute('UPDATE xpsystem SET XP = XP + %s WHERE PlayerUID = %s;', (amount, steamid))

            # Check if it actually changed
            await dzcur.execute('SELECT XP FROM xpsystem WHERE PlayerUID = %s;', (steamid,))
            new = await asyncio.gather(dzcur.fetchone())

            if(new == original):
                await ctx.send("An error has occured! Nothing has been changed. Please fix your syntax")
            else:
                embed = discord.Embed(
                    title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Data:", value=f"{player.mention} has received **{amount} XP**!")
                embed.add_field(
                    name="Original:", value=f"{player.mention} had **{original[0]['XP']} XP**!")
                embed.add_field(
                    name="New:", value=f"{player.mention} now has **{new[0]['XP']} XP**!")
                await ctx.send(embed=embed)
                admin = ctx.message.author
                await DBCommandsCog.amountlog(self, ctx, amount, player, admin, "XP")
        else:
            await ctx.send(f"The DiscordUser: {user.mention} is not registered. Please create a ticket with your SteamID in the subject!")

        # Close Connection
        dzconn.close()

    @commands.command()
    @commands.has_any_role("Owner", "Manager", "Developer", "Head Admin", "Super Admin")
    async def humanity(self, ctx, player: discord.Member, amount: int):
        # Open Connection
        dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
        dzcur = await dzconn.cursor(aiomysql.DictCursor)

        if await DBCommandsCog.check_id(self, player):
            steamid = await DBCommandsCog.get_steamid(self, player)

            embed = discord.Embed(
                title=f"ReactToConfirm \U0001f4b1", colour=discord.Colour(0xFFA500))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(name="Type:", value=f"`Humanity`")
            embed.add_field(name="Amount:", value=f"`{amount}`")
            embed.add_field(name="STEAM64ID:", value=f"`{steamid}`")
            message = await ctx.send(embed=embed)
            await message.add_reaction("\U0001f44d")
            await message.add_reaction("\U0001f44e")

            def reactioncheck(reaction, user):
                validreactions = ["\U0001f44d", "\U0001f44e"]
                return user.id == ctx.author.id and reaction.emoji in validreactions
            reaction, user = await self.bot.wait_for('reaction_add', check=reactioncheck)
            # Check if thumbs up
            if reaction.emoji != "\U0001f44d":
                await ctx.send("Command cancelled")
                return

            # Get starting value
            await dzcur.execute('SELECT Humanity FROM character_data WHERE PlayerUID = %s;', (steamid,))
            original = await asyncio.gather(dzcur.fetchone())

            await dzcur.execute('UPDATE character_data SET Humanity = Humanity + %s WHERE PlayerUID = %s;', (amount, steamid))

            # Check if it actually changed
            await dzcur.execute('SELECT Humanity FROM character_data WHERE PlayerUID = %s;', (steamid,))
            new = await asyncio.gather(dzcur.fetchone())

            if(new == original):
                await ctx.send("An error has occured! Nothing has been changed. Please fix your syntax")
            else:
                embed = discord.Embed(
                    title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Data:", value=f"{player.mention} has received **{amount} Humanity**!")
                embed.add_field(
                    name="Original:", value=f"{player.mention} had **{original[0]['Humanity']} Humanity**!")
                embed.add_field(
                    name="New:", value=f"{player.mention} now has **{new[0]['Humanity']} Humanity**!")
                await ctx.send(embed=embed)
                admin = ctx.message.author
                await DBCommandsCog.amountlog(self, ctx, amount, player, admin, "Humanity")
        else:
            await ctx.send(f"The DiscordUser: {user.mention} is not registered. Please create a ticket with your SteamID in the subject!")

        # Close Connection
        dzconn.close()
    
    @commands.command()
    @commands.has_any_role("Owner", "Manager", "Developer", "Head Admin", "Super Admin", "Admin", "Moderator")
    async def playerdata(self, ctx, player: str):
        '''
        Gets all of a player's data
        '''
        # Open Connection
        dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
        dzcur = await dzconn.cursor(aiomysql.DictCursor)

        if(await DBCommandsCog.validsteamidcheck(self, ctx, player) != True):
            try:
                newuser = await commands.MemberConverter().convert(ctx, player)
            except:
                await ctx.send(f"Invalid value for user: `{player}` (Must be a **Discord User8* or a Valid **STEAM64ID**)")
                return

            # Checks to see if user is registered
            if await DBCommandsCog.check_id(self, newuser):
                steamid = await DBCommandsCog.get_steamid(self, newuser)
                # Get the data
                await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
                bankData = await asyncio.gather(dzcur.fetchone())
                await dzcur.execute('SELECT XP FROM xpsystem WHERE PlayerUID = %s;', (steamid,))
                xpData = await asyncio.gather(dzcur.fetchone())
                await dzcur.execute('SELECT Humanity FROM character_data WHERE PlayerUID = %s;', (steamid,))
                humData = await asyncio.gather(dzcur.fetchone())
                if bankData[0] == None and xpData[0] == None and humData[0] == None:
                    # Check if there is Bank or XP data
                    bankData = 0
                    xpData = 0
                    humData = 0
                else:
                    bankData = bankData[0]['BankCoins']
                    xpData = xpData[0]['XP']
                    humData = humData[0]['Humanity']
                
                embed = discord.Embed(
                    title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(name=f"Player Data:", value=f"**BankCoins**: {bankData}\n"
                                                            f"**XP**: {xpData}\n"
                                                            f"**Humanity**: {humData}\n"
                                                            f"**STEAM64ID**: {steamid}", inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"The DiscordUser: {newuser.mention} is not registered.")
        else:
            # User was a SteamID
            steamid=player
            if(await DBCommandsCog.validsteamidcheck(self, ctx, steamid) != True):
                    # To check if SteamID is valid
                embed=discord.Embed(
                    title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Error:", value=f"Invalid STEAM64ID of: {msg.steamid}")
                await ctx.send(embed=embed)
                return
            await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
            bankData=await asyncio.gather(dzcur.fetchone())
            await dzcur.execute('SELECT XP FROM xpsystem WHERE PlayerUID = %s;', (steamid,))
            xpData=await asyncio.gather(dzcur.fetchone())
            await dzcur.execute('SELECT Humanity FROM character_data WHERE PlayerUID = %s;', (steamid,))
            humData = await asyncio.gather(dzcur.fetchone())
            if bankData[0] == None and xpData[0] == None and humData[0] == 0:
                # Check if there is Bank or XP data
                bankData = 0
                xpData = 0
                humData = 0
            else:
                bankData = bankData[0]['BankCoins']
                xpData = xpData[0]['XP']
                humData = humData[0]['Humanity']

            embed = discord.Embed(
                title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(name=f"Player Data:", value=f"**BankCoins**: {bankData}\n"
                                                        f"**XP**: {xpData}\n"
                                                        f"**Humanity**: {humData}\n"
                                                        f"**STEAM64ID**: {steamid}", inline=False)
            await ctx.send(embed=embed)

        # Close Connection
        dzconn.close()

    @commands.command()
    @commands.has_any_role("Owner", "Developer")
    async def customquery(self, ctx, query: str, db: str):
        if db == "dz":
            # Open Connection
            dzconn=await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
            dzcur=await dzconn.cursor(aiomysql.DictCursor)

            await ctx.send("Are you sure you would like to perform the following? If yes, react with a Thumbs Up. Otherwise, reacting with a Thumbs Down")
            embed=discord.Embed(
                title=f"CustomQueryInfo \U0000270d", colour=discord.Colour(0xFFA500))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(name="Query:", value=f"`{query}`")
            embed.add_field(name="Database:", value=f"`DayZ DB`")
            message=await ctx.send(embed=embed)
            await message.add_reaction("\U0001f44d")
            await message.add_reaction("\U0001f44e")

            def reactioncheck(reaction, user):
                validreactions=["\U0001f44d", "\U0001f44e"]
                return user.id == ctx.author.id and reaction.emoji in validreactions
            reaction, user=await self.bot.wait_for('reaction_add', check=reactioncheck)
            # Check if thumbs up
            if reaction.emoji != "\U0001f44d":
                return
            await dzcur.execute(query)
            await dzconn.commit()
            result=await asyncio.gather(dzcur.fetchall())
            for x in result:
                embed=discord.Embed(
                    title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(name="Data:", value=f"`{x}`")
                await ctx.send(embed=embed)

            # Close Connection
            dzconn.close()

        elif db == "dis":
            await ctx.send("Are you sure you would like to perform the following? If yes, react with a Thumbs Up. Otherwise, reacting with a Thumbs Down")
            embed=discord.Embed(
                title=f"CustomQueryInfo \U0000270d", colour=discord.Colour(0xFFA500))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(name="Query:", value=f"`{query}`")
            embed.add_field(name="Database:", value=f"`Discord DB`")
            message=await ctx.send(embed=embed)
            await message.add_reaction("\U0001f44d")
            await message.add_reaction("\U0001f44e")

            def reactioncheck(reaction, user):
                validreactions=["\U0001f44d", "\U0001f44e"]
                return user.id == ctx.author.id and reaction.emoji in validreactions
            reaction, user = await self.bot.wait_for('reaction_add', check=reactioncheck)
            # Check if thumbs up
            if reaction.emoji != "\U0001f44d":
                return
            await self.bot.discur.execute(query)
            result=await asyncio.gather(self.bot.discur.fetchall())
            for x in result:
                embed=discord.Embed(
                    title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(name="Data:", value=f"`{x}`")
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(DBCommandsCog(bot))
