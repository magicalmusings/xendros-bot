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

APPEND_TAG = "a"
CHAR_DATA_PATH = "data/char_data.json"
READ_TAG = "r"
WRITE_TAG = "w"

class XendrosCog( commands.Cog, name = "Xendros" ):

  def __init__( self, bot ):

    self.bot = bot
    self.CHAR_DATA = {}

    # Import User Data

    with open( CHAR_DATA_PATH, READ_TAG ) as read_file:
      self.CHAR_DATA = json.load( read_file )

    # End __init__() function

  ## Main Functions 

  async def getCharData( self, ctx ):

    with open( CHAR_DATA_PATH , READ_TAG ) as read_file:

      self.CHAR_DATA = json.load( read_file )

  async def updateCharData( self, ctx ):

    with open( CHAR_DATA_PATH, WRITE_TAG ) as write_file:

      json.dump( self.CHAR_DATA, write_file, indent = 4)

  # add() function
  # - adds a character to the database
  @commands.command( name = "add", pass_context = True )
  async def add( self, ctx, *args ):

    await self.bot.wait_until_ready()

    # ERROR CASE(S): If command is given improperly 
    if args is None or len( args ) < 2:
      
      await self.displayErrorMessage( ctx, ERROR_CODES.ADD_ARGS_LENGTH_ERROR )
      return

    char_add_flag = False
    message = ctx.message
    
    # Grab current information from char_data

    await self.getCharData( ctx )

    # ALT CASE: If this is the users first time using Kallista
    if str(message.author.id) not in self.CHAR_DATA:

      await ctx.send( "Seems like it's your first time here, love. Allow me to add you to my registry..." )

      self.CHAR_DATA[str(message.author.id)] = {}
      user_data = self.CHAR_DATA[str(message.author.id)]
      user_data["user_name"] = f"{message.author.name}"
      user_data["active_char"] = "1"
      user_data["1"] = {}
      user_data["2"] = {}
      user_data["3"] = {}
      user_data["4"] = {}
      user_data["5"] = {}

    user_data = self.CHAR_DATA[str(message.author.id)]
    print( user_data )

    # Get the ids of the characters
    char_one = user_data["1"]
    char_two = user_data["2"]
    char_three = user_data["3"]
    char_four = user_data["4"]
    char_five = user_data["5"]

    # ERROR CASE: If three characters are already made 
    if len(char_one) != 0 and len(char_two) != 0 and len(char_three) != 0 and len(char_four) != 0 and len(char_five) != 0:
      await self.displayErrorMessage( ctx, ERROR_CODES.TOO_MANY_CHARS_ERROR )
      return

    char_name = args[0]

    # Set active character to new character
    # Add character default data to the set char

    if len(char_one) == 0 and char_add_flag is False:
      char_add_flag = True
      self.CHAR_DATA[str(message.author.id)]["active_char"] = "1"

    if len(char_two) == 0 and char_add_flag is False:
      char_add_flag = True
      self.CHAR_DATA[str(message.author.id)]["active_char"] = "2"

    if len(char_three) == 0 and char_add_flag is False:
      char_add_flag = True
      self.CHAR_DATA[str(message.author.id)]["active_char"] = "3"

    if len(char_four) == 0 and char_add_flag is False:
      char_add_flag = True
      self.CHAR_DATA[str(message.author.id)]["active_char"] = "4"

    if len(char_five) == 0 and char_add_flag is False:
      char_add_flag = True
      self.CHAR_DATA[str(message.author.id)]["active_char"] = "5"

    # Initialize row for user in char_data table
    active_char_slot = self.CHAR_DATA[str(message.author.id)]["active_char"]

    char_name = args[0]
    drive_link = args[1]

    active_char = self.CHAR_DATA[str(message.author.id)][active_char_slot]
    active_char["char_name"] = f"{char_name}"
    active_char["drive_link"] = f"{drive_link}"
    active_char["gacha_rolls"] = "0"
    active_char["action_points"] = "5"
    active_char["downtime"] = "0"
    active_char["lore_tokens"] = "0"
    active_char["platinum"] = "0"
    active_char["electrum"] = "0"
    active_char["gold"] = "10"
    active_char["silver"] = "0"
    active_char["copper"] = "0"

    await self.updateCharData( ctx )

    await ctx.send( f"You've been added to my list, {char_name}! I've given you 10 gold as a welcome gift. Hopefully ours will be an ongoing arrangement, love.")

    # End add() function 

  # delete function
  # - allows users to delete their registered character with Xendros
  @commands.command( name = "delete", pass_context = True, aliases = ["del", "d"] )
  async def delete( self, ctx, arg = None ):

    await self.bot.wait_until_ready()

    message = ctx.message 

    await self.getCharData( ctx )

    # ERROR CASE: if result is non-existent (no characters registered)
    if arg is None:
      await self.displayErrorMessage( ctx, ERROR_CODES.DELETE_ARGS_LENGTH_ERROR )
      return
    elif str( message.author.id ) not in self.CHAR_DATA:
      return
    elif int(arg) > 5:
      return

    # Get Character ID
    user_data = self.CHAR_DATA[ str( message.author.id ) ]
    char_data = user_data[str(arg)]
    char_slot = str(arg)

    # ERROR CASE: If the specified slot is already empty
    if len( char_data ) == 0:
      await self.displayErrorMessage( ctx, ERROR_CODES.CHAR_SLOT_EMPTY_ERROR )
      return

    # Update Character Slot
    self.CHAR_DATA[ str( message.author.id ) ][char_slot] = {}

    await ctx.send( f"The character in Slot { char_slot } has been deleted." )

    await self.updateCharData( ctx )

    # Check if no more characters exist for this character
    if len( user_data["1"] ) == 0 and len( user_data["2"] ) == 0 and len( user_data["3"] ) == 0 and len( user_data["4"] ) == 0 and len( user_data["5"] ) == 0:

      await ctx.send( "Seeing as you no longer have any characters registered with me, I will be temporarily closing your user account. Please use ```!x add [char_name] [gsheet_link]``` to open another account if you so wish. ")

      await self.erase( ctx, str(message.author.id) )

    # End of delete function

    return

  @commands.command( name = "erase", pass_context = True )
  @commands.is_owner()
  async def erase( self, ctx, arg ):

    await self.bot.wait_until_ready()

    if arg is None:
      return

    message = ctx.message 

    await self.getCharData( ctx )

    if str( message.author.id ) not in self.CHAR_DATA:

      await self.displayErrorMessage( ctx, ERROR_CODES.ERASE_NO_CHAR_ERROR )
      return

    del self.CHAR_DATA[str( message.author.id )]

    await self.updateCharData( ctx )

    await ctx.send( "You have successfully deleted the specified account from my registry. Perhaps we may see them again?")

    # End of Erase Function 

    return

  # switchchar() function 
  # - allows users to switch which active character they are using 
  #   on the Xendros bot 
  @commands.command( name = "switchchar", pass_context = True , aliases = ["sc"])
  async def switchchar( self, ctx, arg = None ):

    # ERROR CASE: if command is not called correctly

    await self.bot.wait_until_ready()

    if arg is None: 
      await self.displayErrorMessage( ctx, ERROR_CODES.SWITCHCHAR_ARGS_LENGTH_ERROR )
      return
    elif int(arg) > 5:
      await self.displayErrorMessage( ctx, ERROR_CODES.SWITCHCHAR_ARGS_LENGTH_ERROR )
      return

    message = ctx.message

    await self.getCharData( ctx )

    # ERROR CASE: If there is no data for the user
    if str( message.author.id ) not in self.CHAR_DATA:
      await self.displayErrorMessage( ctx, ERROR_CODES.USER_ID_NOT_FOUND_ERROR )
      return

    user_data = self.CHAR_DATA[str(message.author.id)]
    active_char_slot = user_data["active_char"]
    active_char = user_data[active_char_slot]

    # ERROR CASE: If the active character is already set 
    if active_char_slot == str(arg):
      await self.displayErrorMessage( ctx, ERROR_CODES.SWITCHCHAR_ACTIVE_SET_ERROR )
      return

    # ERROR CASE: If only one character is registered
    if len( user_data["2"] ) == 0 and len( user_data["3"]) == 0 and len( user_data["4"]) == 0 and len( user_data["5"]) == 0:

      await self.displayErrorMessage( ctx, ERROR_CODES.SWITCHCHAR_ONE_CHAR_ERROR )
      return

    # ERROR CASE: If slot chosen is not filled 
    if len(user_data["1"]) == 0 and arg == 1:

      await self.displayErrorMessage( ctx, ERROR_CODES.SWITCHCHAR_CHAR_SLOT_ONE_ERROR )
      return

    elif len(user_data["2"]) == 0 and arg == 2:

      await self.displayErrorMessage( ctx, ERROR_CODES.SWITCHCHAR_CHAR_SLOT_TWO_ERROR )
      return

    elif len(user_data["3"]) == 0 and arg == 3:

      await self.displayErrorMessage( ctx, ERROR_CODES.SWITCHCHAR_CHAR_SLOT_THREE_ERROR )
      return

    elif len(user_data["4"]) == 0 and arg == 4:

      await self.displayErrorMessage( ctx, ERROR_CODES.SWITCHCHAR_CHAR_SLOT_THREE_ERROR )
      return

    elif len(user_data["5"]) == 0 and arg == 5:

      await self.displayErrorMessage( ctx, ERROR_CODES.SWITCHCHAR_CHAR_SLOT_THREE_ERROR )
      return

    # Display successful switch of character to user 

    user_data["active_char"] = str(arg)
    active_char = user_data[str(arg)]

    char_name = active_char["char_name"]

    await ctx.send( f"Success! I've changed your active character to {char_name}.")

    # End of switchchar() function

    return

  # charlink function
  # - allows users to get google drive link to character at any point
  @commands.command( name = "charlink", pass_context = True , aliases = ['link'])
  async def charlink( self, ctx ):

    await self.bot.wait_until_ready()

    message = ctx.message

    await self.getCharData( ctx )

    # ERROR CASE: If Result is None
    if str(message.author.id) not in self.CHAR_DATA: 
      await self.displayErrorMessage( ctx, ERROR_CODES.USER_ID_NOT_FOUND_ERROR )
      return

    user_data = self.CHAR_DATA[str(message.author.id)]
    active_char_slot = user_data["active_char"]
    active_char = user_data[active_char_slot]

    char_name = active_char["char_name"]
    drive_link = active_char["drive_link"]

    await ctx.send( f"Hello { char_name }! Here is the link to your character sheet (whatever that is...):")
    await ctx.send( f"{ drive_link }" )

    return

  @commands.command( name = "charlist", pass_context = True , aliases = ["list"] )
  async def charlist( self, ctx ): 

    await self.bot.wait_until_ready()
    
    message = ctx.message

    await self.getCharData( ctx )

    # ERROR CASE: If result is none
    if str(message.author.id) not in self.CHAR_DATA: 
      await self.displayErrorMessage( ctx, ERROR_CODES.USER_ID_NOT_FOUND_ERROR )
      return 

    embed = discord.Embed(
      title = f"Characters for { message.author }",
      color = discord.Color.dark_blue()
    )

    user_data = self.CHAR_DATA[str(message.author.id)]

    if len( user_data["1"] ) != 0:
      char_name = user_data["1"]["char_name"]
      embed.add_field( name = "Character Slot 1", 
                       value = f"{char_name}",
                       inline = False )
    elif len( user_data["1"] ) == 0:
      embed.add_field( name = "Character Slot 1",
                       value = "NONE",
                       inline = False )
    if len( user_data["2"] ) != 0:
      char_name = user_data["2"]["char_name"]
      embed.add_field( name = "Character Slot 2", 
                       value = f"{char_name}",
                       inline = False )
    elif len( user_data["2"] ) == 0:
      embed.add_field( name = "Character Slot 2",
                       value = "NONE",
                       inline = False )
    if len( user_data["3"] ) != 0:
      char_name = user_data["3"]["char_name"]
      embed.add_field( name = "Character Slot 3", 
                       value = f"{char_name}",
                       inline = False )
    elif len( user_data["3"] ) == 0:
      embed.add_field( name = "Character Slot 3",
                       value = "NONE",
                       inline = False )
    if len( user_data["4"] ) != 0:
      char_name = user_data["4"]["char_name"]
      embed.add_field( name = "Character Slot 4", 
                       value = f"{char_name}",
                       inline = False )
    elif len( user_data["4"] ) == 0:
      embed.add_field( name = "Character Slot 4",
                       value = "NONE",
                       inline = False )
    if len( user_data["5"] ) != 0:
      char_name = user_data["5"]["char_name"]
      embed.add_field( name = "Character Slot 5", 
                       value = f"{char_name}",
                       inline = False )
    elif len( user_data["5"] ) == 0:
      embed.add_field( name = "Character Slot 5",
                       value = "NONE",
                       inline = False )

    await ctx.send( embed = embed )

    # End of charlist() function 
    return 

# End Xendros Cog

def setup( bot ):
  bot.add_cog( XendrosCog( bot ) )
  print( '------\nXendros Cog has been loaded!\n------' )
