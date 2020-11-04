
import discord
from discord.ext import commands
import disputils
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import re
import sqlite3

# OLD COG FOR SHOPKEEPING - DEPRECATED
# Kept in Source Code for Reference on:
#  - Discord Command Cog formatting 
#  - .json file interaction 
#  - Google Sheet integrations

APPEND_TAG = "a"
BUYBACK_DATA_PATH = "data/buyback.json"
CART_DATA_PATH = "data/carts.json"
CHAR_DATA_PATH = "data/char_data.sqlite"
GSHEET_CREDS_PATH = "data/raw/Kallista Xendros-41faef61ff65.json"
READ_TAG = "r"
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file',
'https://www.googleapis.com/auth/drive']
SHOP_CLOSED = 0
SHOP_OPEN = 1
USER_CHARS_PATH = "data/user_chars.sqlite"
WRITE_TAG = "w"

class ShopkeepCog( commands.Cog , name = "Shopkeeping" ):

  def __init__( self, bot ):

    #  : Fix user_chars table 
    #  : Fix char_data table
    #  : delete json files
    #  : remove gsheet integration

    self.bot = bot
  
    with open( CART_DATA_PATH , READ_TAG ) as json_file:
      self.cart_data = json.load( json_file )

    with open( BUYBACK_DATA_PATH, READ_TAG ) as json_file:
      self.buyback_data = json.load( json_file )

    creds = ServiceAccountCredentials.from_json_keyfile_name( GSHEET_CREDS_PATH, SCOPE )
    self.gsheet_client = gspread.authorize( creds )

    db = sqlite3.connect( USER_CHARS_PATH )
    cursor = db.cursor()
    cursor.execute( '''CREATE TABLE IF NOT EXISTS user_chars(
      user_id integer PRIMARY KEY,
      active_char integer DEFAULT 1,
      char_one_id integer DEFAULT 0,
      char_two_id integer DEFAULT 0,
      char_three_id integer DEFAULT 0
    );''')
    cursor.close()
    db.close()

    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( ''' CREATE TABLE IF NOT EXISTS char_data(
      char_id integer PRIMARY KEY,
      user_id integer DEFAULT 0,
      drive_link text,
      char_name text,
      silver integer DEFAULT 0,
      lore_token integer DEFAULT 0,
      purchases integer DEFAULT 0,
      gacha_rolls integer DEFAULT 0,
      shop_open integer DEFAULT 0,
      shop_type text,
      shop_tier integer DEFAULT 1
    );''' )
    cursor.close()
    db.close()

  async def update_jsons( self ):
    await self.bot.wait_until_ready()

    with open( CART_DATA_PATH , WRITE_TAG ) as json_file:
      json.dump( self.buyback_data, json_file, indent = 4 )

    with open( BUYBACK_DATA_PATH, WRITE_TAG ) as json_file:
      json.dump( self.buyback_data, json_file, indent = 4 )

  @commands.command( name = "add", pass_context = True )
  async def add( self, ctx, arg = None ):

    #  : Fix Add

    if arg is None:
      await ctx.send( "I need a url for tracking inventory, darling. Try running the command again like this: ```!x add <gsheet url>")
      return

    char_add_flag = False
    message = ctx.message
    db = sqlite3.connect( USER_CHARS_PATH )
    cursor = db.cursor()
    cursor.execute( f"SELECT user_id, char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{ message.author.id }'")

    result = cursor.fetchone()

    # If this is the users first time using Kallista
    if result is None:
      await ctx.send( "Seems like it's your first time here, love. Allow me to add you to my registry...")

      # Initialize data for user in user_chars table
      sql = ("""INSERT INTO user_chars(
        user_id, active_char, char_one_id, char_two_id, char_three_id ) VALUES (?,?,?,?,?) """ )
      values = ( message.author.id, 1, 0, 0, 0)
      cursor.execute( sql, values )
      db.commit()

      cursor.execute( f"SELECT user_id, char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{ message.author.id }'")
      result = cursor.fetchone()
      
    # Get the ids of the characters
    char_one_id = int( result[1] )
    char_two_id = int( result[2] )
    char_three_id = int( result[3] )

    # If three characters are already made
    if char_one_id != 0 and char_two_id != 0 and char_three_id != 0:
      await ctx.send( "Darling, you already have three characters registered with me. How many more do you need? Consider deleting one using ```!x delete <char_number>```" )
      cursor.close()
      db.close()
      return

    # Access Passed In Google Sheet
    try:
      sheet = self.gsheet_client.open_by_url( arg ).sheet1
    except:
      await ctx.send( "Hmm...Unfortunately I cannot access this spreadsheet. Have you by chance shared it with the following address? ```automagic@kallista-xendros.iam.gserviceaccount.com```")
      db = sqlite3.connect( USER_CHARS_PATH )
      cursor = db.cursor()
      cursor.execute( f"DELETE FROM user_chars WHERE user_id = '{message.author.id}'")
      db.commit()
      cursor.close()
      db.close()
      return

    new_id = await self.generate_char_id()
    char_name = sheet.cell( 6, 3 ).value

    db = sqlite3.connect( USER_CHARS_PATH )
    cursor = db.cursor()

    if char_one_id == 0 and char_add_flag is False:
      char_add_flag = True
      sql = ( """UPDATE user_chars SET char_one_id = ? WHERE user_id = ?""")

    if char_two_id == 0 and char_add_flag is False:
      char_add_flag = True
      sql = ( """UPDATE user_chars SET char_two_id = ? WHERE user_id = ?""")

    if char_three_id == 0 and char_add_flag is False:
      char_add_flag = True
      sql = ( """UPDATE user_chars SET char_three_id = ? WHERE user_id = ?""")

    values = ( new_id, message.author.id )
    cursor.execute( sql, values )
    db.commit()

    # Initialize row for user in char_data table
    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    sql = ("""INSERT INTO char_data(
      char_id, user_id, drive_link, char_name, silver, lore_token, purchases, gacha_rolls, shop_open, shop_type, shop_tier
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?) """)
    values = ( new_id, message.author.id, arg, char_name, 50, 0, 0, 0, 0, "NONE", 1)
    cursor.execute( sql, values )
    db.commit()
      
    await ctx.send( f"You've been added to my list, {char_name}! I've given you 50 silver as a welcome gift. Hopefully ours will be an ongoing arrangement, love.")

    cursor.close()
    db.close()

  async def generate_char_id( self ):

    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    generated_id = 1

    cursor.execute( f"SELECT char_id from char_data WHERE char_id = '{generated_id}'")
    result = cursor.fetchone()
    while result is not None:
      generated_id += 1
      cursor.execute( f"SELECT char_id from char_data WHERE char_id = '{generated_id}'")
      result = cursor.fetchone()

    return generated_id

  @commands.command( name = "switchchar", pass_context = True )
  async def switchchar( self, ctx, arg = None ):

    #  : Fix switchchar

    if arg is None:
      await ctx.send( "Alas darling, you must tell me which character you'd like to switch to. Try using the command like this: ```!x switchchar <char_slot>```")
      return

    message = ctx.message
    
    db = sqlite3.connect( USER_CHARS_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT active_char from user_chars WHERE user_id = '{message.author.id}' """ )
    result = cursor.fetchone()

    if result is None:
      await ctx.send( "I don't seem to have any characters registered with you. Please try to add a character using ```!x add <gsheet_url>```")
      cursor.close()
      db.close()
      return

    active_char = int( result[0] )

    if active_char == arg:
      await ctx.send( f"I have already set your active character to Character Slot {arg}. No need to tell me twice!")
      cursor.close()
      db.close()
      return

    cursor.execute( f"""SELECT active_char, char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{message.author.id}'""" )
    result = cursor.fetchone()

    active_char = int( result[0] )
    char_one_id = int( result[1] )
    char_two_id = int( result[2] )
    char_three_id = int( result[3] )

    # Error Case: if only one character is registered
    if char_two_id == 0 and char_three_id == 0:
      await ctx.send( "You only have one character registered with me, love. Consider adding another using ```!x add <gsheet url>```")
      cursor.close()
      db.close()
      return

    # Error case: If slot chosen is not filled
    if char_one_id == 0 and arg == 1:
      await ctx.send( "You do not have a character registered with Slot 1. Consider adding another using ```!x add <gsheet url>```")
      cursor.close()
      db.close()
      return
    elif char_two_id == 0 and arg == 2:
      await ctx.send( "You do not have a character registered with Slot 2. Consider adding another using ```!x add <gsheet url>```")
      cursor.close()
      db.close()
      return
    elif char_three_id == 0 and arg == 3:
      await ctx.send( "You do not have a character registered with Slot 3. Consider adding another using ```!x add <gsheet url>```")
      cursor.close()
      db.close()
      return

    sql = (""" UPDATE user_chars SET active_char = ? WHERE user_id = ? """)
    values = ( arg, message.author.id )
    cursor.execute( sql, values )
    db.commit()

    cursor.execute( f"""SELECT active_char, char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{message.author.id}'""" )
    result = cursor.fetchone()

    active_char = int( result[0] )
    char_one_id = int( result[1] )
    char_two_id = int( result[2] )
    char_three_id = int( result[3] )

    if active_char == 1:
      active_char_id = char_one_id
    elif active_char == 2:
      active_char_id = char_two_id
    elif active_char == 3:
      active_char_id = char_three_id

    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT char_name FROM char_data WHERE char_id = '{active_char_id}'""" )
    result = cursor.fetchone()

    char_name = str( result[0] )

    await ctx.send( f"Success! I've changed your active character to {char_name}.")

    cursor.close()
    db.close()
    
  @commands.command( name = "balance", pass_context = True )
  async def balance( self, ctx ):

    #  : Fix Balance

    message = ctx.message

    db = sqlite3.connect( USER_CHARS_PATH )
    cursor = db.cursor()
    cursor.execute( f"SELECT active_char, char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{ message.author.id }'")

    result = cursor.fetchone()

    if result is None:
      await ctx.send( "Hmm, it seems it's your first time in my shop. Please register with me using ```!x add <character name> <gsheet link>```")
      cursor.close()
      db.close()
      return

    active_char = int( result[0] )

    if active_char == 1:
      char_id = int( result[1] )
    elif active_char == 2:
      char_id = int( result[2] )
    elif active_char == 3:
      char_id = int( result[3] )

    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"SELECT user_id, char_name, silver, lore_token, purchases, gacha_rolls FROM char_data WHERE char_id = '{char_id}'")
    result = cursor.fetchone()

    user_id = int( result[0] )
    char_name = str( result[1] )
    silver = int( result[2] )
    lt = int( result[3] )
    purchases = int( result[4] )
    gacha_rolls = int( result[5] )

    embed = discord.Embed(
      title = f'{char_name}'
    )
    embed.add_field( name = "Current Balance", value = f"{silver} Silver", inline = True )
    embed.add_field( name = "Loremaster Tokens (LT)", value = f"{lt} LT", inline = True )
    embed.add_field( name = "Total Items Purchases", value = f"{purchases}", inline = False )
    embed.add_field( name = "Gacha Rolls Made", value = f"{gacha_rolls}", inline = True )
    embed.set_footer( text = f"Character ID: {char_id}, User ID: {user_id}" )

    await ctx.send( f"Hello {char_name}! Here's your current data on file:")
    await ctx.send( embed = embed )

    cursor.close()
    db.close()

  @commands.command( name = "deposit", pass_context = True )
  @commands.is_owner()
  async def deposit( self, ctx, *args ):

    #  : Fix deposit

    if len( args ) < 2:
      await ctx.send( "Unfortunately, you've messed up the command. Try running it this way:```!x deposit <char_id> <amount>")
      return

    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT silver FROM char_data WHERE char_id = '{args[0]}' """ )
    result = cursor.fetchone()

    if result is None:
      await ctx.send( "Hmm, it seems I don't have that user on my list. Please have them register with me using ```!x add <gsheet url>```")
      cursor.close()
      db.close()
      return

    silver = int( result[0] )

    sql = ("""UPDATE char_data SET silver = ? WHERE char_id = ?""")
    values = ( silver + int(args[1]), int(args[0]) )
    cursor.execute( sql, values )
    db.commit()

    cursor.execute( f"""SELECT char_name, silver FROM char_data WHERE char_id = '{args[0]}' """ )

    result = cursor.fetchone()
    char_name = str(result[0])
    silver = str(result[1])

    await ctx.send( f"Fantastic, I've deposited {args[1]} silver into {char_name}'s account. Their new balance is {silver} silver!" )

    cursor.close()
    db.close()

  @commands.command( name = "withdraw", pass_context = True )
  @commands.is_owner()
  async def withdraw( self, ctx, *args ):

    #  : Fix withdraw

    if len( args ) < 2:
        await ctx.send( "Unfortunately, you've messed up the command. Try running it this way:```!x withdraw <char_id> <amount>")
        return

    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT silver FROM char_data WHERE char_id = '{args[0]}' """ )
    result = cursor.fetchone()

    if result is None:
      await ctx.send( "Hmm, it seems I don't have that user on my list. Please have them register with me using ```!x add <gsheet url>```")
      cursor.close()
      db.close()
      return

    silver = int( result[0] ) - int( args[1] )
    if silver < 0:
      silver = 0

    sql = ("""UPDATE char_data SET silver = ? WHERE char_id = ?""")
    values = ( silver, int(args[0]) )
    cursor.execute( sql, values )
    db.commit()

    cursor.execute( f"""SELECT char_name, silver FROM char_data WHERE char_id = '{args[0]}' """ )

    result = cursor.fetchone()
    char_name = str(result[0])
    silver = str(result[1])

    await ctx.send( f"Excellent, I've removed {args[1]} silver from {char_name}'s account. Their new balance is {silver} silver!" )

    cursor.close()
    db.close()

  @commands.command( name = "setbal", pass_context = True )
  @commands.is_owner()
  async def setbal( self, ctx, *args ):

    #  : Fix setbal

    if len( args ) < 2:
      await ctx.send( "You've fudged up the numbers a smidge. Try running it this way:```!x setbal <char_id> <amount>")
      return

    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT silver FROM char_data WHERE char_id = '{args[0]}' """ )
    result = cursor.fetchone()

    if result is None:
      await ctx.send( "Hmm, it seems I don't have that user on my list. Please have them register with me using ```!x add <gsheet url>```")
      cursor.close()
      db.close()
      return

    sql = ("""UPDATE char_data SET silver = ? WHERE char_id = ?""")
    values = ( int(args[1]), int(args[0]) )
    cursor.execute( sql, values )
    db.commit()

    cursor.execute( f"""SELECT char_name, silver FROM char_data WHERE char_id = '{args[0]}' """ )

    result = cursor.fetchone()
    char_name = str(result[0])
    silver = str(result[1])

    await ctx.send( f"Done, {char_name}'s new balance is {silver} silver!" )

    cursor.close()
    db.close()

def setup( bot ):
  bot.add_cog( ShopkeepCog( bot ))
  print( '------\nShopkeeping Cog has been loaded!\n------')