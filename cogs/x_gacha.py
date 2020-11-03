import csv
import enum
import json
import math
import os
from copy import copy
from datetime import datetime
from random import randint

# NOTE: pylint error disables are used solely for local development, when ran in Repl.it, Kallista will have these modules available. 

import discord # pylint: disable=import-error
import disputils # pylint: disable=import-error
from discord.ext import commands # pylint: disable=import-error
from jsonmerge import merge # pylint: disable=import-error

import x_error
from x_error import ERROR_CODES

READ_TAG = "r"

# Gacha Roll To Do List: 

# TODO: Implement legendary item rolls
# TODO: Implement legendary item rolls (debug)

class XendrosGachaCog( commands.cog, name = "XendrosGacha" ):

    def __init__( self, bot ):

        self.bot = bot 
        
        self.UC_ROLL_COST = 275
        self.R_ROLL_COST = 2750
        self.VR_ROLL_COST = 27500
        self.L_ROLL_COST = 50000

        self.UNCOMMON_ITEMS = {}
        self.UNCOMMON_ITEMS_PATH = "data/uncommon.json"
        self.RARE_ITEMS = {}
        self.RARE_ITEMS_PATH = "data/rare.json"
        self.VERYRARE_ITEMS = {}
        self.VERYRARE_ITEMS_PATH = "data/veryrare.json"
        self.LEGENDARY_ITEMS = {}
        self.LEGENDARY_ITEMS_PATH = "data/legendary.json"

        # Import Magic Item Data

        await self.loadGachaItemLists()

        print( "Initialization of Gacharoll Cog Complete!")

    async def loadGachaItemLists( self ):

        # Uncommon Items 

        with open( self.UNCOMMON_ITEMS_PATH, READ_TAG ) as read_file:
            self.UNCOMMON_ITEMS = json.load( read_file )

        print( f"Loaded {len(self.UNCOMMON_ITEMS['uncommon'])} uncommon magic items!" )

        # Rare Items

        with open( self.RARE_ITEMS_PATH, READ_TAG ) as read_file:
            self.RARE_ITEMS = json.load( read_file )

        print( f"Loaded {len(self.RARE_ITEMS['rare'])} rare magic items!" )

        # Very Rare Items 

        with open( self.VERYRARE_ITEMS_PATH, READ_TAG ) as read_file:
            self.VERYRARE_ITEMS = json.load( read_file )

        print( f"Loaded {len(self.VERYRARE_ITEMS['veryrare'])} very rare magic items!" )

        return
        # End of loadGachaItemLists() function

    async def displayGachaItemEmbed( self, ctx , item ):

        # Get item data
        item_name = item["name"]
        item_attn = item["attn"]
        item_desc = item["desc"]

        # Prep Item Embed for sending to user
        embed = discord.Embed(
            title = item_name,
            color = discord.Color.green()
            )
        embed.add_field( name = "Requires Attunement?",
                         value = item_attn,
                         inline = False )
        embed.add_field( name = "Description",
                         value = item_desc,
                         inline = False )

        # Display Item to user
        await ctx.send( embed = embed )

        return 
        # End of displayGachaItemEmbed() function
    
    ## Gacharoll Functions

    @commands.group( name = "gacharoll", pass_context = True, aliases = ["gr"] )
    async def gacharoll( self, ctx ):

        if ctx.invoked_subcommand is None:

            await self.displayErrorMessage( ctx, ERROR_CODES.GACHAROLL_SUBCOMMAND_ERROR )
            return 

    # rollUncommon function
    @gacharoll.command( name = "uncommon", pass_context = True, aliases = ["UC", "uc"])
    async def rollUncommon( self, ctx, arg = None ):

        await self.bot.wait_until_ready()

        message = ctx.message
        total_items = len(self.UNCOMMON_ITEMS['uncommon'])

        # Get Character Data 
        await self.getCharData(ctx)

        # Check if user is registered 

        # ERROR CASE: If result is none (i.e. user is not registered)
        if str( message.author.id ) not in self.CHAR_DATA:
            await self.displayErrorMessage( ctx, ERROR_CODES.USER_ID_NOT_FOUND_ERROR )
            return 

        user_data = self.CHAR_DATA[str(message.author.id)]
        active_char_slot = user_data["active_char"]
        active_char = user_data[active_char_slot]

        gold = int(active_char["gold"])
        gacha_rolls = int(active_char["gacha_rolls"])

        # ERROR CASE: Not enough money to roll
        if gold < self.UC_ROLL_COST:
            await self.displayErrorMessage( ctx, ERROR_CODES.GACHAROLL_NOT_ENOUGH_MONEY_ERROR )
            return

        # Subtract money from balance
        # Update gacha_rolls variable

        active_char["gold"] = str(gold - self.UC_ROLL_COST)
        active_char["gacha_rolls"] = str( gacha_rolls + 1)

        # Get Random Number 
        await ctx.send( f"Rolling for { total_items } potential items...")
        roll = randint( 1, total_items)
        await ctx.send( f"Pulled { roll }! Grabbing item from the archives...")

        # Find item 
        item = self.UNCOMMON_ITEMS['uncommon'][str(roll)]

        await self.displayGachaItemEmbed( ctx, item )

        await self.updateCharData(ctx)

        # End of rollUncommon() function
        return 

    # rollRare function
    @gacharoll.command( name = "rare", pass_context = True, aliases = ["R", "r"])
    async def rollRare( self, ctx , arg = None ): 

        await self.bot.wait_until_ready()

        message = ctx.message
        total_items = len(self.RARE_ITEMS['rare'])

        # Get Character Data 
        await self.getCharData( ctx )

        # Check if user is registered 

        # ERROR CASE: If result is none (i.e. user is not registered)
        if str( message.author.id) not in self.CHAR_DATA:
            await self.displayErrorMessage( ctx, ERROR_CODES.USER_ID_NOT_FOUND_ERROR )
            return 

        user_data = self.CHAR_DATA[str(message.author.id)]
        active_char_slot = user_data["active_char"]
        active_char = user_data[active_char_slot]

        gold = int(active_char["gold"])
        gacha_rolls = int(active_char["gacha_rolls"])

        # ERROR CASE: Not enough money to roll
        if gold < self.R_ROLL_COST:
            await self.displayErrorMessage( ctx, ERROR_CODES.GACHAROLL_NOT_ENOUGH_MONEY_ERROR )
            return

        # Subtract money from balance
        # Update gacha_rolls variable

        active_char["gold"] = str(gold - self.R_ROLL_COST)
        active_char["gacha_rolls"] = str( gacha_rolls + 1)

        # Get Random Number 
        await ctx.send( f"Rolling for { total_items } potential items...")
        roll = randint( 1, total_items)
        await ctx.send( f"Pulled { roll }! Grabbing item from the archives...")

        # Find item 
        item = self.RARE_ITEMS['rare'][str(roll)]

        await self.displayGachaItemEmbed( ctx, item )

        await self.updateCharData( ctx )

        # End of rollRare() function
        return 

    # rollVeryRare function
    @gacharoll.command( name = "veryrare", pass_context = True, aliases = ["vr", "VR"])
    async def rollVeryRare( self, ctx, arg = None ):

        await self.bot.wait_until_ready()

        message = ctx.message
        total_items = len(self.VERYRARE_ITEMS['veryrare'])

        # Get Character Data 
        await self.getCharData( ctx )

        # Check if user is registered 

        # ERROR CASE: If result is none (i.e. user is not registered)
        if str( message.author.id ) not in self.CHAR_DATA:
            await self.displayErrorMessage( ctx, ERROR_CODES.USER_ID_NOT_FOUND_ERROR )
            return 

        user_data = self.CHAR_DATA[str(message.author.id)]
        active_char_slot = user_data["active_char"]
        active_char = user_data[active_char_slot]

        gold = int(active_char["gold"])
        gacha_rolls = int(active_char["gacha_rolls"])

        # ERROR CASE: Not enough money to roll
        if gold < self.VR_ROLL_COST:
            await self.displayErrorMessage( ctx, ERROR_CODES.GACHAROLL_NOT_ENOUGH_MONEY_ERROR )
            return

        # Subtract money from balance
        # Update gacha_rolls variable

        active_char["gold"] = str(gold - self.VR_ROLL_COST)
        active_char["gacha_rolls"] = str( gacha_rolls + 1)

        # Get Random Number 
        await ctx.send( f"Rolling for { total_items } potential items...")
        roll = randint( 1, total_items)
        await ctx.send( f"Pulled { roll }! Grabbing item from the archives...")

        # Find item 
        item = self.VERYRARE_ITEMS['veryrare'][str(roll)]

        await self.displayGachaItemEmbed( ctx, item )

        await self.updateCharData( ctx )

        # End of rollVeryRare() function
        return 
 
    # GachaAdmin Command Group
    @commands.group( name = "gachadebug", pass_context = True , aliases = ["gd"])
    @commands.is_owner()
    async def gachadebug( self, ctx ):

        if ctx.invoked_subcommand is None:
            await self.displayErrorMessage( ctx, ERROR_CODES.GACHAADMIN_SUBCOMMAND_ERROR)
            return

    # rollUncommon_admin function
    @gachadebug.command( name = "uca", pass_context = True )
    @commands.is_owner()
    async def rollUncommonAdmin( self, ctx, arg = None ):

        await self.bot.wait_until_ready()

        total_items = len(self.UNCOMMON_ITEMS['uncommon'])

        # Get Random Number 
        await ctx.send( f"Rolling for { total_items } potential items...")
        roll = randint( 1, total_items)
        await ctx.send( f"Pulled { roll }! Grabbing item from the archives...")

        # Find item 
        item = self.UNCOMMON_ITEMS['uncommon'][str(roll)]

        await self.displayGachaItemEmbed( ctx, item )

        # End of rollUncommonAdmin() function
        return 

    # rollRare_admin function
    @gachadebug.command( name = "ra", pass_context = True )
    @commands.is_owner()
    async def rollRareAdmin( self, ctx, arg = None ):

        await self.bot.wait_until_ready()

        total_items = len(self.RARE_ITEMS['rare'])

        # Get Random Number 
        await ctx.send( f"Rolling for { total_items } potential items...")
        roll = randint( 1, total_items)
        await ctx.send( f"Pulled { roll }! Grabbing item from the archives...")

        # Find item 
        item = self.RARE_ITEMS['rare'][str(roll)]

        await self.displayGachaItemEmbed( ctx, item )

        # End of rollRareAdmin() function
        return 

    # rollVeryRare_admin
    @gachadebug.command( name = "vra", pass_context = True )
    @commands.is_owner()
    async def rollVeryRareAdmin( self, ctx, arg = None ):

        await self.bot.wait_until_ready()

        total_items = len(self.VERYRARE_ITEMS['veryrare'])

        # Get Random Number 
        await ctx.send( f"Rolling for { total_items } potential items...")
        roll = randint( 1, total_items)
        await ctx.send( f"Pulled { roll }! Grabbing item from the archives...")

        # Find item 
        item = self.VERYRARE_ITEMS['veryrare'][str(roll)]

        await self.displayGachaItemEmbed( ctx, item )

        # End of rollVeryRareAdmin() function
        return 

def setup( bot ):
    bot.add_cog( XendrosGachaCog( bot ) )
    print( '------\nGacha Cog has been loaded!\n------')