import csv
import enum
import json
import math
import os
import sqlite3
from datetime import datetime
from random import randint

# NOTE: pylint error disables are used solely for local development, when ran in Repl.it, Kallista will have these modules available. 

import discord # pylint: disable=import-error
import disputils # pylint: disable=import-error
from discord.ext import commands # pylint: disable=import-error
from jsonmerge import merge # pylint: disable=import-error
from nested_lookup import nested_lookup # pylint: disable=import-error

APPEND_TAG = "a"
CHAR_DATA_PATH = "data/char_data.json"
CURRENCY_SWITCH = {
      'ap': "action_points",
      'cp': "copper",
      'dt': "downtime",
      'ep': "electrum",
      'gp': "gold",
      'lt': "lore_tokens",
      'pp': "platinum",
      'sp': 'silver'
}
L_ROLL_COST = 50000
LEGENDARY_ITEMS = {}
LEGENDARY_ITEMS_PATH = "data/legendary.json"
R_ROLL_COST = 2750
RARE_ITEMS = {}
RARE_ITEMS_PATH = "data/rare.json"
READ_TAG = "r"
UC_ROLL_COST = 275
UNCOMMON_ITEMS = {}
UNCOMMON_ITEMS_PATH = "data/uncommon.json"
VR_ROLL_COST = 27500
VERYRARE_ITEMS = {}
VERYRARE_ITEMS_PATH = "data/veryrare.json"
WRITE_TAG = "w"

class ERROR_CODES( enum.Enum ):
  NO_ERROR = 0
  ADD_ARGS_LENGTH_ERROR = 1
  USER_ID_NOT_FOUND_ERROR = 2
  CHAR_ID_NOT_FOUND_ERROR = 3
  TOO_MANY_CHARS_ERROR = 4
  DELETE_ARGS_LENGTH_ERROR = 5
  CHAR_SLOT_EMPTY_ERROR = 6
  ERASE_NO_CHAR_ERROR = 7
  SWITCHCHAR_ARGS_LENGTH_ERROR = 8
  SWITCHCHAR_ACTIVE_SET_ERROR = 9
  SWITCHCHAR_CHAR_SLOT_ONE_ERROR = 10
  SWITCHCHAR_CHAR_SLOT_TWO_ERROR = 11
  SWITCHCHAR_CHAR_SLOT_THREE_ERROR = 12
  SWITCHCHAR_ONE_CHAR_ERROR = 13
  BALANCE_URL_ERROR = 14
  DEPOSIT_ARGS_LENGTH_ERROR = 15
  DEPOSIT_CURRENCY_ERROR = 16
  WITHDRAW_ARGS_LENGTH_ERROR = 17
  WITHDRAW_CURRENCY_ERROR = 18
  SETBAL_ARGS_LENGTH_ERROR = 19
  SETBAL_CURRENCY_ERROR = 20
  GACHAROLL_SUBCOMMAND_ERROR = 21
  GACHAROLL_NOT_ENOUGH_MONEY_ERROR = 22
  GACHAADMIN_SUBCOMMAND_ERROR = 23
  CURREX_ARGS_LENGTH_ERROR = 24
  CURREX_INVALID_CURRENCY_ERROR = 25
  CURREX_DOWNTIME_INPUT_ERROR = 26
  CURREX_INVALID_CONVERSION_ERROR = 27
  CURREX_NO_CONVERSION_NEEDED_ERROR = 28
  CURREX_AP_LT_CONVERSION_ERROR = 29
  CURREX_NOT_ENOUGH_CURRENCY_ERROR = 30

class XendrosCog( commands.Cog, name = "Xendros" ):

  def __init__( self, bot ):

    self.bot = bot

    # Import User Data

    with open( CHAR_DATA_PATH, READ_TAG ) as read_file:
      self.CHAR_DATA = json.load( read_file )

    # Import Magic Item Data

    # Uncommon Items 

    with open( UNCOMMON_ITEMS_PATH, READ_TAG ) as read_file:
      global UNCOMMON_ITEMS
      UNCOMMON_ITEMS = json.load( read_file )

    print( f"Loaded {len(UNCOMMON_ITEMS['uncommon'])} uncommon magic items!" )

    # Rare Items

    with open( RARE_ITEMS_PATH, READ_TAG ) as read_file:
      global RARE_ITEMS
      RARE_ITEMS = json.load( read_file )

    print( f"Loaded {len(RARE_ITEMS['rare'])} rare magic items!" )

    # End __init__() function

  ## Main Functions 

  async def getCharData( self, ctx ):

    with open( CHAR_DATA_PATH , READ_TAG ) as read_file:

      self.CHAR_DATA = json.load( read_file )

  async def updateCharData( self, ctx ):

    with open( CHAR_DATA_PATH, WRITE_TAG ) as write_file:

      json.dump( self.CHAR_DATA, write_file, indent = 4)

  async def displayErrorMessage( self, ctx, error_code ):

    error_messages = {
      ERROR_CODES.NO_ERROR: "No Error",
      ERROR_CODES.ADD_ARGS_LENGTH_ERROR:"I need a name and url for tracking inventory, darling. Try running the command again like this: ```!x add <char_name> <gsheet url> ```",
      ERROR_CODES.USER_ID_NOT_FOUND_ERROR: "I don't seem to have any characters registered with your user ID. Please attempt to add a character using ```!x add <char_name> <gsheet_url>```",
      ERROR_CODES.CHAR_ID_NOT_FOUND_ERROR:"There seems to be a mistake here. I do not have your character on file. Please attempt to add a character using ```!x add <char_name> <gsheet_url>```",
      ERROR_CODES.TOO_MANY_CHARS_ERROR: "Darling, you already have three characters registered with me. How many more do you need? Consider deleting one using ```!x delete <char_number>```",
      ERROR_CODES.DELETE_ARGS_LENGTH_ERROR: "Alas darling, you must tell me which character you'd like to delete to. Try using the command like this: ```!x delete <char_slot>```",
      ERROR_CODES.CHAR_SLOT_EMPTY_ERROR: "Unfortunately, I cannot delete that which does not exist. That character slot is currently empty in my books.",
      ERROR_CODES.ERASE_NO_CHAR_ERROR: "Unfortunately, I cannot erase that which does not exist. That user is not currently registered in my books.",
      ERROR_CODES.SWITCHCHAR_ARGS_LENGTH_ERROR: "Alas darling, you must tell me which character you'd like to switch to. Try using the command like this: ```!x switchchar <char_slot>```",
      ERROR_CODES.SWITCHCHAR_ACTIVE_SET_ERROR: f"I have already set your active character to this character slot. No need to tell me twice!",
      ERROR_CODES.SWITCHCHAR_CHAR_SLOT_ONE_ERROR: "You do not have a character registered with Slot 1. Consider adding another using ```!x add <char_name> <gsheet url>```",
      ERROR_CODES.SWITCHCHAR_CHAR_SLOT_TWO_ERROR: "You do not have a character registered with Slot 2. Consider adding another using ```!x add <char_name> <gsheet url>```",
      ERROR_CODES.SWITCHCHAR_CHAR_SLOT_THREE_ERROR: "You do not have a character registered with Slot 3. Consider adding another using ```!x add <char_name> <gsheet url>```",
      ERROR_CODES.SWITCHCHAR_ONE_CHAR_ERROR: "You only have one character registered with me, love. Consider adding another using ```!x add <char_name> <gsheet url>```",
      ERROR_CODES.BALANCE_URL_ERROR: "The url given for this character is broken. Consider deleting and resubmitting information using ```!x delete <char_slot>\n!x add <char_name> <gsheet url>```",
      ERROR_CODES.DEPOSIT_ARGS_LENGTH_ERROR: "Unfortunately, you've messed up the command. Try running it this way:```!x deposit <char_id> <currency> <amount>```",
      ERROR_CODES.DEPOSIT_CURRENCY_ERROR: "That is not a currency that I can currently track. Consider retyping the command with a valid currency",
      ERROR_CODES.WITHDRAW_ARGS_LENGTH_ERROR: "Unfortunately, you've messed up the command. Try running it this way:```!x withdraw <char_id> <currency> <amount>```",
      ERROR_CODES.WITHDRAW_CURRENCY_ERROR: "That is not a currency that I can currently track. Consider retyping the command with a valid currency",
      ERROR_CODES.SETBAL_ARGS_LENGTH_ERROR: "Unfortunately, you've messed up the command. Try running it this way:```!x withdraw <char_id> <currency> <amount>```",
      ERROR_CODES.SETBAL_CURRENCY_ERROR: "That is not a currency that I can currently track. Consider retyping the command with a valid currency",
      ERROR_CODES.GACHAROLL_SUBCOMMAND_ERROR: "Invalid subcommand passed... please try using the command like ```!x gacharoll <rarity>```",
      ERROR_CODES.GACHAROLL_NOT_ENOUGH_MONEY_ERROR: "Seems like you don't have enough gold to roll... Come back when you're not broke!",
      ERROR_CODES.GACHAADMIN_SUBCOMMAND_ERROR: "Invalid subcommand passed... please try using the command like ```!x gachaadmin <rarity>```",
      ERROR_CODES.CURREX_ARGS_LENGTH_ERROR: "Sorry, I can't convert any currency with this information. Try using the command like this: ```!x currex <curr_one> <curr_two>```",
      ERROR_CODES.CURREX_INVALID_CURRENCY_ERROR: "That is not a currency that I can currently track. Consider retyping the command with a valid currency",
      ERROR_CODES.CURREX_DOWNTIME_INPUT_ERROR: "I cannot convert downtime into money, unfortunately. Consider retyping the command with a valid currency",
      ERROR_CODES.CURREX_INVALID_CONVERSION_ERROR: "I cannot convert AP / LT into money, or vice versa. Consider retyping the command with a valid currency",
      ERROR_CODES.CURREX_NO_CONVERSION_NEEDED_ERROR: "Silly! Conversion between the same currency is unnecessary.",
      # TODO: Implement ap/lt conversion function 
      ERROR_CODES.CURREX_AP_LT_CONVERSION_ERROR: "I cannot convert AP to LT or vice versa with this command. Please consider using another in order to do so. ",
      ERROR_CODES.CURREX_NOT_ENOUGH_CURRENCY_ERROR: "There is unfortunately not enough currency to convert. Consider checking your balance using ```!x balance``` before attempting another conversion.",

    }

    error_msg_str = error_messages.get( error_code, "CODE NOT FOUND" )

    if error_msg_str == "CODE NOT FOUND":
      print( "ERROR CODE NOT FOUND, RETURNING EMPTY STRING")
      error_msg_str = ""

    await ctx.send( error_msg_str )

    return

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
    elif arg > 5:
      await self.displayErrorMessage( ctx, ERROR_CODES.SWITCHCHAR_ARGS_LENGTH_ERROR )
      return

    message = ctx.message

    await self.getCharData( ctx )

    # ERROR CASE: If there is no data for the user
    if str( message.author.id ) not in self.CHAR_DATA:
      await self.displayErrorMessage( ctx, ERROR_CODES.USER_ID_NOT_FOUND_ERROR )
      return

    user_data = self.CHAR_DATA( message.author.id )
    active_char_slot = user_data["active_char"]
    active_char = user_data[active_char_slot]

    # ERROR CASE: If the active character is already set 
    if active_char_slot == str(arg):
      await self.displayErrorMessage( ctx, ERROR_CODES.SWITCHCHAR_ACTIVE_SET_ERROR )
      return

    # Get character ids from user_chars table 

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

  
  ## Money / Currency Functions 

  # balance function
  @commands.command( name = "balance", pass_context = True , aliases = ['bal'])
  async def balance( self, ctx ):

    message = ctx.message

    await self.getCharData( ctx )

    # ERROR CASE: If the player has not yet registered with the bot
    if str(message.author.id) not in self.CHAR_DATA:
      await self.displayErrorMessage( ctx, ERROR_CODES.USER_ID_NOT_FOUND_ERROR )
      return

    # Find Active Character
    user_data = self.CHAR_DATA[str(message.author.id)]

    active_char_slot = user_data["active_char"]
    active_char = user_data[active_char_slot]

    user_id = str(message.author.id)
    drive_link = active_char["drive_link"]
    char_name = active_char["char_name"]
    action_points = int(active_char["action_points"])
    downtime = int(active_char["downtime"])
    lore_tokens = int(active_char["lore_tokens"])
    platinum = int(active_char["platinum"])
    electrum = int(active_char["electrum"])
    gold = int(active_char["gold"])
    silver = int(active_char["silver"])
    copper = int(active_char["copper"])
    gacha_rolls = int(active_char["gacha_rolls"])

    # Create Embed for display
    try: 
      embed = discord.Embed(
        title = f'{ char_name }',
        url = f'{ drive_link }',
        color = discord.Color.dark_green()
      )
      embed.add_field( name = "Action Points",
                      value = f"{ action_points } AP",
                      inline = True )
      embed.add_field( name = "Downtime",
                      value = f"{ downtime } DT",
                      inline = True )
      embed.add_field( name = "Loremaster Tokens",
                      value = f"{ lore_tokens } LT",
                      inline = True )      
      embed.add_field( name = "Current Balance",
                      value = f"{platinum} pp, {electrum} ep, {gold} gp, {silver} sp, {copper} cp",
                      inline = False )
      embed.add_field( name = "Total Gacha Rolls Made",
                      value = f"{ gacha_rolls }",
                      inline = True ) 
      embed.set_footer( text = f"User ID: {user_id}, Char Slot: {active_char_slot}")
    except:
      await self.displayErrorMessage( ctx, ERROR_CODES.BALANCE_URL_ERROR )
      return

    await ctx.send( embed = embed )    

    # End of balance() function

  # deposit function 
  @commands.command( name = "deposit", pass_context = True , aliases = ['dep'])
  @commands.is_owner()
  async def deposit( self, ctx, *args ):

    await self.bot.wait_until_ready()

    # ERROR CASE: If # of arguments is not correct
    if len( args ) < 3:
      await self.displayErrorMessage( ctx, ERROR_CODES.DEPOSIT_ARGS_LENGTH_ERROR )
      return

    currency = CURRENCY_SWITCH.get( args[1], "NULL")

    # ERROR CASE: If input currency is invalid
    if currency == "NULL":

      await self.displayErrorMessage( ctx, ERROR_CODES.DEPOSIT_CURRENCY_ERROR )
      return

    await self.getCharData( ctx )

    # ERROR CASE: If result is null 
    try:
      char_data = nested_lookup( args[0], self.CHAR_DATA )
    except:
      await self.displayErrorMessage( ctx, ERROR_CODES.CHAR_ID_NOT_FOUND_ERROR )
      return 

    print( char_data )
    
    current_amt = int( char_data.get(currency) )

    char_data[currency] = str( current_amt + int( args[2] ) )

    char_name = str(char_data["char_name"])
    new_amt = str(char_data[currency])

    await ctx.send( f"Fantastic, I've deposited { args[2] } { args[1].upper() } into {char_name}'s account. Their new balance is {new_amt} { args[1].upper() } !")

    await self.updateCharData( ctx )

    # End of deposit() function 

    return 

  # withdraw function
  @commands.command( name = "withdraw", pass_context = True )
  @commands.is_owner()
  async def withdraw( self, ctx, *args ):

    # ERROR CASE: If # of arguments is not correct
    if len( args ) < 3:
      await self.displayErrorMessage( ctx, ERROR_CODES.WITHDRAW_ARGS_LENGTH_ERROR )
      return

    currency = CURRENCY_SWITCH.get( args[1], "NULL")

    if currency == "NULL":

      await self.displayErrorMessage( ctx, ERROR_CODES.WITHDRAW_CURRENCY_ERROR )
      return

    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT { currency } FROM char_data WHERE char_id = '{args[0]}' """)
    result = cursor.fetchone()

    if result is None:

      await self.displayErrorMessage( ctx, ERROR_CODES.USER_ID_NOT_FOUND_ERROR )
      cursor.close()
      db.close()
      return

    current_amt = int( result[0])

    sql = ( f"""UPDATE char_data SET {currency} = ? WHERE char_id = ?""")
    if current_amt - int( args[2] ) < 0:
      new_amt = 0
    else:
      new_amt = current_amt - int( args[2] )
    values = ( new_amt, int(args[0]) )
    cursor.execute( sql, values )
    db.commit()

    cursor.execute( f"""SELECT char_Name, {currency} FROM char_data WHERE char_id = '{args[0]}'""" )
    result = cursor.fetchone()

    char_name = str(result[0])
    new_amt = str(result[1])

    await ctx.send( f"I've withdrawn { args[2] } { args[1].upper() } from {char_name}'s account. Their new balance is {new_amt} { args[1].upper() } !")

    cursor.close() 
    db.close() 

    # End of withdraw() function

  # setbal function
  @commands.command( name = "setbal", pass_context = True , aliases = ['sb'])
  async def setbal( self, ctx, *args ):

    # ERROR CASE: If # of arguments is not correct
    if len( args ) < 3:
      await self.displayErrorMessage( ctx, ERROR_CODES.SETBAL_ARGS_LENGTH_ERROR )
      return

    currency = CURRENCY_SWITCH.get( args[1], "NULL")

    if currency == "NULL":

      await self.displayErrorMessage( ctx, ERROR_CODES.SETBAL_CURRENCY_ERROR )
      return

    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT { currency } FROM char_data WHERE char_id = '{args[0]}' """)
    result = cursor.fetchone()

    if result is None:

      await self.displayErrorMessage( ctx, ERROR_CODES.USER_ID_NOT_FOUND_ERROR )
      cursor.close()
      db.close()
      return

    current_amt = int( result[0])

    sql = ( f"""UPDATE char_data SET {currency} = ? WHERE char_id = ?""")
    values = ( int(args[2]), int(args[0]) )
    cursor.execute( sql, values )
    db.commit()

    cursor.execute( f"""SELECT char_Name, {currency} FROM char_data WHERE char_id = '{args[0]}'""" )
    result = cursor.fetchone()

    char_name = str(result[0])
    new_amt = str(result[1])

    await ctx.send( f"Great, I've set {char_name}'s {currency.upper()} amount from {current_amt} {args[1].upper()} to { new_amt} { args[1].upper() } !")

    cursor.close() 
    db.close() 

    # End of setbal() function

    return 

  # currex function
  @commands.command( name = "currex", pass_context = True, aliases = ["cx"] )
  async def currex( self, ctx, *args ):
    # EX USAGE: !x currex <currency_one> <currency_two>

    # ERROR CASE: if # of args is incorrect
    if len( args ) < 3:
      await self.displayErrorMessage( ctx, ERROR_CODES.CURREX_ARGS_LENGTH_ERROR )
      return 

    message = ctx.message

    # Get user char data 
    db = sqlite3.connect( USER_CHARS_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT active_char, char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{ message.author.id }'""")
    result = cursor.fetchone()

    # ERROR CASE: If user is not registered
    if result is None:
      await self.displayErrorMessage( ctx, ERROR_CODES.USER_ID_NOT_FOUND_ERROR )
      cursor.close()
      db.close()
      return

    active_char = int( result[0] )
    char_one_id = int( result[1] )
    char_two_id = int( result[2] )
    char_three_id = int( result[3] )

    if active_char == 1:
      char_id = char_one_id
    elif active_char == 2:
      char_id = char_two_id
    elif active_char == 3:
      char_id = char_three_id

    amt_to_convert = int( args[0] )
    currency_one = CURRENCY_SWITCH.get( args[1], "NULL")
    currency_two = CURRENCY_SWITCH.get( args[2], "NULL")

    # ERROR CASE: If input currency is invalid
    if currency_one == "NULL" or currency_two == "NULL":
      await self.displayErrorMessage( ctx, ERROR_CODES.CURREX_INVALID_CURRENCY_ERROR )
      cursor.close()
      db.close()
      return

    # ERROR CASE: If downtime is attempted for conversion
    elif currency_one == "downtime" or currency_two == "downtime":
      await self.displayErrorMessage( ctx, ERROR_CODES.CURREX_DOWNTIME_INPUT_ERROR )
      cursor.close()
      db.close()
      return

    elif currency_one == "action_points" or currency_one == "lore_tokens" or currency_two == "action_points" or currency_two == "lore_tokens":
      await self.displayErrorMessage( ctx, ERROR_CODES.CURREX_AP_LT_CONVERSION_ERROR )
      cursor.close()
      db.close()
      return

    # ERROR CASE: If ap / lt and pp/ep/gp/sp/cp are being converted between.
    elif (currency_one == "action_points" or currency_one == "lore_tokens") and (currency_two == "platinum" or currency_two == "gold" or currency_two == "silver" or currency_two == "copper" or currency_two == "electrum"):
      await self.displayErrorMessage( ctx, ERROR_CODES.CURREX_INVALID_CONVERSION_ERROR )
      cursor.close()
      db.close()
      return

    elif (currency_two == "action_points" or currency_two == "lore_tokens") and (currency_one == "platinum" or currency_one == "gold" or currency_one == "silver" or currency_one == "copper" or currency_one == "electrum"):
      await self.displayErrorMessage( ctx, ERROR_CODES.CURREX_INVALID_CONVERSION_ERROR )
      cursor.close()
      db.close()
      return

    # Check current balance
    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"SELECT {currency_one}, {currency_two} FROM char_data WHERE char_id = '{char_id}'")
    result = cursor.fetchone()

    # ERROR CASE: If character does not exist
    if result is None:
      await self.displayErrorMessage( ctx, ERROR_CODES.CHAR_ID_NOT_FOUND_ERROR )
      cursor.close()
      db.close()
      return

    # Check amt of first currency
    curr_one_amt = int( result[0] )

    # ERROR CASE: if we don't have enough currency in order to make it work
    if curr_one_amt == 0:
      # Error message 
      cursor.close()
      db.close()
      return 

    # If we don't have enough currency, but still have currency:
    #  - use what's left to convert. 
    if curr_one_amt - amt_to_convert < 0:
      await ctx.send( f"Oops, looks like you don't have all the currency to convert. I'll just use the **{curr_one_amt}** {currency_one} that's left in your account." )
      amt_to_convert = curr_one_amt

    curr_two_amt = int( result[1] )

    conversion_chart = {
      "platinum": {
        "platinum": 1,
        "electrum": 20,
        "gold": 10,
        "silver": 100,
        "copper": 1000
      },
      "electrum": {
        "platinum": 0.05,
        "electrum": 1,
        "gold": 0.5,
        "silver": 5,
        "copper": 50
      },
      "gold": {
        "platinum": 0.1,
        "electrum": 2,
        "gold": 1,
        "silver": 10,
        "copper": 100
      },
      "silver": {
        "platinum": 0.01,
        "electrum": 0.2,
        "gold": 0.1,
        "silver": 1,
        "copper": 10
      },
      "copper": {
        "platinum": 0.001,
        "electrum": 0.02,
        "gold": 0.01,
        "silver": 0.1,
        "copper": 1
      }
    }

    conversion_rate = conversion_chart[currency_one][currency_two]
    backwards_conversion_rate = conversion_chart[currency_two][currency_one]

    # ERROR CASE: Converting between the same currency
    if conversion_rate == 1 or backwards_conversion_rate == 1:
      await self.displayErrorMessage( ctx, ERROR_CODES.CURREX_NO_CONVERSION_NEEDED_ERROR )
      cursor.close()
      db.close()
      return
    
    # Examples of conversion are included below. For the purposes of examples, lets say the user currently has: 
    # - curr_one_amt = 12 pp
    # - curr_two_amt = 100 gp

    # Calculate amt of currency to add to currency_two
    # Ex: for 12 pp -> gp , 12pp x 10 (pp->gp conversion rate) = 120 gp to add
    curr_to_add = math.floor( amt_to_convert * conversion_rate )

    # ERROR CASE: 
    if curr_to_add <= 0:
      await self.displayErrorMessage( ctx, ERROR_CODES.CURREX_NOT_ENOUGH_CURRENCY_ERROR )
      cursor.close()
      db.close()
      return

    # Add amt of currency to new currency_two total 
    # Ex: for 12 pp -> gp, 100 + 120 = 220 (new_curr_two_amt)
    new_curr_two_amt = curr_two_amt + ( curr_to_add )

    # Calculate amt of currency to remove from currency_one
    # Ex: for 12 pp -> gp, floor( 120 * 0.1 ) = 12 pp to subtract
    curr_to_subtract = math.floor( curr_to_add * backwards_conversion_rate )

    # Subtract amt of currency from currency_one total 
    # Ex: for 12 pp -> gp, 12 - 12 = 0 remaining pp 
    new_curr_one_amt = curr_one_amt - ( curr_to_subtract )

    # Update character data 
    sql = ( f"""UPDATE char_data SET {currency_one} = ?, {currency_two} = ? WHERE char_id = ?""")
    values = ( new_curr_one_amt, new_curr_two_amt, char_id )
    cursor.execute( sql, values )
    db.commit()

    # Display conversion success and balance to user
    await ctx.send( f"Success! I've converted your **{amt_to_convert}** {currency_one} into **{curr_to_add}** {currency_two}!! Your new balance is: ")
    await self.balance( ctx )

    # close out database
    cursor.close()
    db.close()

    # End of currex function
    return



    arg = args[0]
    await ctx.send( arg )
    await ctx.send( type( arg ) )
    
    if arg is None:
      # DUMP_ARG_LENGTH_ERROR
      await ctx.send( "returned ")
      return
    elif arg != "user_chars" and arg != "char_data":
      # DUMP_INVALID_DB_ERROR
      await ctx.send( "returned" )
      return

    await ctx.send( "C1: Checked Args")

    if arg == "user_chars":
      path = USER_CHARS_DATA_PATH
      sql = ("""SELECT user_name, user_id, active_char, char_one_id, char_two_id, char_three_id FROM user_chars ORDER BY user_name """)
    elif arg == "char_data":
      path = CHAR_DATA_PATH
      sql = ("""SELECT char_name, char_id, user_id, drive_link, action_points, downtime, lore_tokens, platinum, electrum, gold, silver, copper, gacha_rolls FROM char_data ORDER BY char_name """)

    await ctx.send( "C2: Set path and SQL commands ")

    db = sqlite3.connect( path )
    cursor = db.cursor()
    cursor.execute( sql )
    result = cursor.fetchall()

    await ctx.send( "C3: Fetched data from database")

    headers = [i[0] for i in cursor.description]

    await ctx.send( "C4: Autogenerated headers")

    date = datetime.now()
    dt_str = date.strftime("%d_%m_%y_%h_%m_%s")

    await ctx.send( "C5: Got date")

    csvFile = csv.writer( open( f"data/dump/{arg}_{dt_str}.csv", WRITE_TAG, newline=''), delimiter=',', lineterminator='\r\n', quoting=csv.QUOTE_ALL, escapechar='\\')

    await ctx.send( "C6: Created csv file in data directory ")

    csvFile.writerow( headers )
    csvFile.writerows( result )

    print( 'data export successful')

    await ctx.send( "Data Export Successful!")

    cursor.close()
    db.close()

    return
    
  
  ## Gacharoll Functions

  @commands.group( name = "gacharoll", pass_context = True, aliases = ["gr"] )
  async def gacharoll( self, ctx ):

    if ctx.invoked_subcommand is None:

      await self.displayErrorMessage( ctx, ERROR_CODES.GACHAROLL_SUBCOMMAND_ERROR )
      return 

  # rollUncommon function
  @gacharoll.command( name = "uncommon", pass_context = True, aliases = ["UC", "uc"])
  async def rollUncommon( self, ctx, arg = None ):

    message = ctx.message
    total_items = len(UNCOMMON_ITEMS['uncommon'])

    # Get Character Data 

    # Check if user is registered 
    db = sqlite3.connect( USER_CHARS_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT active_char, char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{ message.author.id }'""")
    result = cursor.fetchone()

    # ERROR CASE: If result is none (i.e. user is not registered)
    if result is None:
      await self.displayErrorMessage( ctx, ERROR_CODES.USER_ID_NOT_FOUND_ERROR )
      cursor.close()
      db.close()
      return 

    active_char = int( result[0] )
    char_one_id = int( result[1] )
    char_two_id = int( result[2] )
    char_three_id = int( result[3] )

    if active_char == 1:
      char_id = char_one_id
    elif active_char == 2:
      char_id = char_two_id
    elif active_char == 3:
      char_id = char_three_id

    # Check current balance
    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"SELECT gold, gacha_rolls FROM char_data WHERE char_id = '{char_id}'")
    result = cursor.fetchone()

    if result is None:
      await self.displayErrorMessage( ctx, ERROR_CODES.CHAR_ID_NOT_FOUND_ERROR )
      cursor.close()
      db.close()
      return

    gold = int( result[0] )
    gacha_rolls = int( result[1] )

    # ERROR CASE: Not enough money to roll
    if gold < UC_ROLL_COST:
      await self.displayErrorMessage( ctx, ERROR_CODES.GACHAROLL_NOT_ENOUGH_MONEY_ERROR )
      cursor.close()
      db.close()
      return

    # Subtract money from balance
    # Update gacha_rolls variable

    sql = ( """UPDATE char_data SET gold = ?, gacha_rolls = ? WHERE char_id = ? """)
    values = ( gold - UC_ROLL_COST, gacha_rolls + 1, char_id )
    cursor.execute( sql, values )
    db.commit()

    # Get Random Number 
    await ctx.send( f"Rolling for { total_items } potential items...")
    roll = randint( 1, total_items)
    await ctx.send( f"Pulled { roll }! Grabbing item from the archives...")

    # Find item 
    item = UNCOMMON_ITEMS['uncommon'][str(roll)]

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

    cursor.close()
    db.close()

    # End of rollUncommon() function
    return 

  # rollRare function
  @gacharoll.command( name = "rare", pass_context = True, aliases = ["R", "r"])
  async def rollRare( self, ctx , arg = None ): 

    message = ctx.message
    total_items = len(RARE_ITEMS['rare'])

    # Get Character Data 

    # Check if user is registered 
    db = sqlite3.connect( USER_CHARS_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT active_char, char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{ message.author.id }'""")
    result = cursor.fetchone()

    # ERROR CASE: If result is none (i.e. user is not registered)
    if result is None:
      await self.displayErrorMessage( ctx, ERROR_CODES.USER_ID_NOT_FOUND_ERROR )
      cursor.close()
      db.close()
      return 

    active_char = int( result[0] )
    char_one_id = int( result[1] )
    char_two_id = int( result[2] )
    char_three_id = int( result[3] )

    if active_char == 1:
      char_id = char_one_id
    elif active_char == 2:
      char_id = char_two_id
    elif active_char == 3:
      char_id = char_three_id

    # Check current balance
    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"SELECT gold, gacha_rolls FROM char_data WHERE char_id = '{char_id}'")
    result = cursor.fetchone()

    if result is None:
      await self.displayErrorMessage( ctx, ERROR_CODES.CHAR_ID_NOT_FOUND_ERROR )
      cursor.close()
      db.close()
      return 

    gold = int( result[0] )
    gacha_rolls = int( result[1] )

    # ERROR CASE: Not enough money to roll
    if gold < R_ROLL_COST:
      await self.displayErrorMessage( ctx, ERROR_CODES.GACHAROLL_NOT_ENOUGH_MONEY_ERROR )
      cursor.close()
      db.close()
      return

    # Subtract money from balance
    # Update gacha_rolls variable

    sql = ( """UPDATE char_data SET gold = ?, gacha_rolls = ? WHERE char_id = ? """)
    values = ( gold - R_ROLL_COST, gacha_rolls + 1, char_id )
    cursor.execute( sql, values )
    db.commit()

    # Get Random Number 
    await ctx.send( f"Rolling for { total_items } potential items...")
    roll = randint( 1, total_items)
    await ctx.send( f"Pulled { roll }! Grabbing item from the archives...")

    # Find item 
    item = RARE_ITEMS['rare'][str(roll)]

    # Get item data
    item_name = item["name"]
    item_attn = item["attn"]
    item_desc = item["desc"]

    # Prep Item Embed for sending to user
    embed = discord.Embed(
      title = item_name,
      color = discord.Color.blue()
    )
    embed.add_field( name = "Requires Attunement?",
                     value = item_attn,
                     inline = False )
    embed.add_field( name = "Description",
                     value = item_desc,
                     inline = False )

    # Display Item to user
    await ctx.send( embed = embed )

    cursor.close()
    db.close()

    # End of rollUncommon() function
    return 

  # rollVeryRare function  

  # rollLegendary function
  
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

    total_items = len(UNCOMMON_ITEMS['uncommon'])

    # Get Random Number 
    await ctx.send( f"Rolling for { total_items } potential items...")
    roll = randint( 1, total_items)
    await ctx.send( f"Pulled { roll }! Grabbing item from the archives...")

    # Find item 
    item = UNCOMMON_ITEMS['uncommon'][str(roll)]

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

    # End of rollUncommon() function
    return 

  # rollRare_admin function
  @gachadebug.command( name = "ra", pass_context = True )
  @commands.is_owner()
  async def rollRareAdmin( self, ctx, arg = None ):

    total_items = len(RARE_ITEMS['rare'])

    # Get Random Number 
    await ctx.send( f"Rolling for { total_items } potential items...")
    roll = randint( 1, total_items)
    await ctx.send( f"Pulled { roll }! Grabbing item from the archives...")

    # Find item 
    item = RARE_ITEMS['rare'][str(roll)]

    # Get item data
    item_name = item["name"]
    item_attn = item["attn"]
    item_desc = item["desc"]

    # Prep Item Embed for sending to user
    embed = discord.Embed(
      title = item_name,
      color = discord.Color.blue()
    )
    embed.add_field( name = "Requires Attunement?",
                     value = item_attn,
                     inline = False )
    embed.add_field( name = "Description",
                     value = item_desc,
                     inline = False )

    # Display Item to user
    await ctx.send( embed = embed )

    # End of rollUncommon() function
    return 

  # rollVeryRare_admin
  
  # rollLegendary_admin


# End Xendros Cog

def setup( bot ):
  bot.add_cog( XendrosCog( bot ) )
  print( '------\nXendros Cog has been loaded!\n------')
