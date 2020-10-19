import discord
from discord.ext import commands
import disputils
import json
from jsonmerge import merge
from random import randint
import sqlite3

APPEND_TAG = "a"
CHAR_DATA_PATH = "data/char_data.sqlite"
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
R_ROLL_COST = 2500
RARE_ITEMS = {}
RARE_ITEMS_PATH = "data/rare.json"
READ_TAG = "r"
UC_ROLL_COST = 250
UNCOMMON_ITEMS = {}
UNCOMMON_ITEMS_PATH = "data/uncommon.json"
USER_CHARS_DATA_PATH = "data/user_chars.sqlite"
VR_ROLL_COST = 25000
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

class XendrosCog( commands.Cog, name = "Xendros" ):

  def __init__( self, bot ):

    self.bot = bot

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

    # Import / Create SQL Databases 

    # User Characters Database 
    db = sqlite3.connect( USER_CHARS_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( '''CREATE TABLE IF NOT EXISTS user_chars(
      user_id integer PRIMARY KEY,
      active_char integer DEFAULT 1,
      char_one_id integer DEFAULT 0,
      char_two_id integer DEFAULT 0,
      char_three_id integer DEFAULT 0
    );
    ''')
    cursor.close()
    db.close()

    # Character Data Database 
    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( '''CREATE TABLE IF NOT EXISTS char_data(
      char_id integer PRIMARY KEY,
      user_id integer DEFAULT 0,
      drive_link text,
      char_name text,
      action_points integer DEFAULT 0,
      downtime integer DEFAULT 0,
      lore_tokens integer DEFAULT 0,
      platinum integer DEFAULT 0,
      electrum integer DEFAULT 0,
      gold integer DEFAULT 0,
      silver integer DEFAULT 0,
      copper integer DEFAULT 0,
      gacha_rolls integer DEFAULT 0
    );
    ''')
    cursor.close()
    db.close()

    # End __init__() function

  ## Main Functions 

  async def displayErrorMessage( self, ctx, error_code = ERROR_CODES.NO_ERROR ):

    error_messages = {
      NO_ERROR = "No Error",
      ADD_ARGS_LENGTH_ERROR = "I need a name and url for tracking inventory, darling. Try running the command again like this: ```!x add <char_name> <gsheet url> ```",
      USER_ID_NOT_FOUND_ERROR = "I don't seem to have any characters registered with your user ID. Please attempt to add a character using ```!x add <char_name> <gsheet_url>```",
      CHAR_ID_NOT_FOUND_ERROR = "There seems to be a mistake here. I do not have your character on file. Please attempt to add a character using ```!x add <char_name> <gsheet_url>",
      TOO_MANY_CHARS_ERROR = "Darling, you already have three characters registered with me. How many more do you need? Consider deleting one using ```!x delete <char_number>```",
      DELETE_ARGS_LENGTH_ERROR = "Alas darling, you must tell me which character you'd like to delete to. Try using the command like this: ```!x delete <char_slot>```",
      CHAR_SLOT_EMPTY_ERROR = "Unfortunately, I cannot delete that which does not exist. That character slot is currently empty in my books.",
      ERASE_NO_CHAR_ERROR = "Unfortunately, I cannot erase that which does not exist. That user is not currently registered in my books.",
      SWITCHCHAR_ARGS_LENGTH_ERROR = "Alas darling, you must tell me which character you'd like to switch to. Try using the command like this: ```!x switchchar <char_slot>```",
      SWITCHCHAR_ACTIVE_SET_ERROR = f"I have already set your active character to this character slot. No need to tell me twice!",
      SWITCHCHAR_CHAR_SLOT_ONE_ERROR = "You do not have a character registered with Slot 1. Consider adding another using ```!x add <char_name> <gsheet url>```",
      SWITCHCHAR_CHAR_SLOT_TWO_ERROR = "You do not have a character registered with Slot 2. Consider adding another using ```!x add <char_name> <gsheet url>```",
      SWITCHCHAR_CHAR_SLOT_THREE_ERROR = "You do not have a character registered with Slot 3. Consider adding another using ```!x add <char_name> <gsheet url>```",
      SWITCHCHAR_ONE_CHAR_ERROR = "You only have one character registered with me, love. Consider adding another using ```!x add <char_name> <gsheet url>```",

    }

    error_msg_str = error_messages.get( error_code, "CODE NOT FOUND" )

    if error_msg_str == "CODE NOT FOUND":
      
      print( "ERROR CODE NOT FOUND, RETURNING EMPTY STRING")
      error_msg_str = ""
      return

    await ctx.send( error_msg_str )

    return

  # add() function
  # - adds a character to the database
  @commands.command( name = "add", pass_context = True )
  async def add( self, ctx, *args ):

    # ERROR CASE(S): If command is given improperly 
    if args is None or len( args ) < 2:
      
      displayErrorMessage( self, ctx, ARGS_LENGTH_ERROR )
      return

    char_add_flag = False
    message = ctx.message
    
    # Grab current information from user_chars table 

    db = sqlite3.connect( USER_CHARS_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( 
      f"SELECT user_id, active_char, char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{ user_id }'")

    result = cursor.fetchone()

    # ALT CASE: If this is the users first time using Kallista
    if result is None:

      await ctx.send( "Seems like it's your first time here, love. Allow me to add you to my registry..." )

      # Initialize data for user in user_chars table 

      sql = ("""
      INSERT INTO user_chars(
        user_id, active_char, char_one_id, char_two_id, char_three_id
      ) VALUES ( ? , ? , ? , ? , ? )
      """)
      values = ( message.author.id, 1, 0, 0, 0 )
      cursor.execute( sql, values )
      db.commit()

      cursor.execute( f"SELECT user_id, char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{ message.author.id }'")
      result = cursor.fetchone()

    # Get the ids of the characters
    char_one_id = int( result[1] )
    char_two_id = int( result[2] )
    char_three_id = int( result[3] )

    # ERROR CASE: If three characters are already made 
    if char_one_id !=0 and char_two_id != 0 and char_three_id != 0:
      displayErrorMessage( self, ctx, TOO_MANY_CHARS_ERROR )
      cursor.close()
      db.close()
      return

    new_id = await self.generate_char_id()
    char_name = args[0]

    db = sqlite3.connect( USER_CHARS_DATA_PATH )
    cursor = db.cursor()

    # Set active character to new character 

    if char_one_id == 0 and char_add_flag is False:
      char_add_flag = True
      sql = ("""UPDATE user_chars SET char_one_id = ? WHERE user_id = ? """)

    if char_two_id == 0 and char_add_flag is False:
      char_add_flag = True
      sql = ("""UPDATE user_chars SET char_two_id = ? WHERE user_id = ? """)

    if char_three_id == 0 and char_add_flag is False:
      char_add_flag = True
      sql = ("""UPDATE user_chars SET char_three_id = ? WHERE user_id = ? """)

    values = ( new_id, message.author.id )
    cursor.execute( sql, values )
    db.commit()
    cursor.close()
    db.close()

    # Initialize row for user in char_data table

    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    sql = ("""
    INSERT INTO char_data(
      char_id, user_id, drive_link, char_name, action_points, downtime, lore_tokens, platinum, electrum, gold, silver, copper, gacha_rolls
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """)
    values = ( new_id, message.author.id, args[1], char_name, 5, 0, 0, 0, 0, 10, 0, 0, 0 )
    cursor.execute( sql, values )
    db.commit()

    await ctx.send( f"You've been added to my list, {char_name}! I've given you 10 gold as a welcome gift. Hopefully ours will be an ongoing arrangement, love.")

    cursor.close()
    db.close()

    # End add() function 

  # generate_char_id() function 
  #  - Support function for add(), generates character id for inputting into char_data table without conflicts
  async def generate_char_id( self ):

    # Get char data from table 
    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    generated_id = 1

    # iterate through and find largest char id
    cursor.execute( f"SELECT char_id from char_data WHERE char_id = '{generated_id}'")
    result = cursor.fetchone()
    while result is not None:
      generated_id += 1
      cursor.execute( f"SELECT char_id from char_data WHERE char_id = '{generated_id}'")
      result = cursor.fetchone()

    return generated_id

    # end generate_char_id() function 

  # delete function
  # - allows users to delete their registered character with Xendros
  @commands.command( name = "delete", pass_context = True, aliases = ["del", "d"] )
  async def delete( self, ctx, arg = None ):

    # TODO: Implement delete function

    message = ctx.message 

    db = sqlite3.connect( USER_CHARS_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{ message.author.id }' """)
    result = cursor.fetchone()

    # ERROR CASE: if result is non-existent (no characters registered)
    if result is None:
      displayErrorMessage( self, ctx, DELETE_ARGS_LENGTH_ERROR )
      cursor.close()
      db.close()
      return

     # Get Character ID
    char_slot = int( arg )

    # ERROR CASE: If the specified slot is already empty
    char_one_id = int( result[0] )
    if char_one_id == 0 and char_slot == 1:
      displayErrorMessage( self, ctx, CHAR_SLOT_EMPTY_ERROR )
      cursor.close()
      db.close()
      return

    char_two_id = int( result[1] )
    if char_two_id == 0 and char_slot == 2:
      displayErrorMessage( self, ctx, CHAR_SLOT_EMPTY_ERROR )
      cursor.close()
      db.close()
      return

    char_three_id = int( result[2] )
    
    if char_three_id == 0 and char_slot == 3:
      displayErrorMessage( self, ctx, CHAR_SLOT_EMPTY_ERROR )
      cursor.close()
      db.close()
      return

    # Update Character Slot
    if char_slot == 1:
        cursor.execute( f"""UPDATE user_chars SET char_one_id = 0 WHERE user_id = '{ message.author.id }'""")
        db.commit()
    elif char_slot == 2:
        cursor.execute( f"""UPDATE user_chars SET char_two_id = 0 WHERE user_id = '{ message.author.id }'""")
        db.commit()
    elif char_slot == 3:
        cursor.execute( f"""UPDATE user_chars SET char_three_id = 0 WHERE user_id = '{ message.author.id }'""")
        db.commit()

    await ctx.send( f"The character in Slot { char_slot } has been deleted." )

    cursor.execute( f"""SELECT char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{ message.author.id }' """)
    result = cursor.fetchone()

    # Check if no more characters exist for this character
    char_one_id = int( result[0] )
    char_two_id = int( result[1] )
    char_three_id = int( result[2] )
    if char_one_id == 0 and char_two_id == 0 and char_three_id == 0:

      cursor.execute( f"""DELETE FROM user_chars WHERE user_id = '{message.author.id}' """)
      await ctx.send( "Seeing as you no longer have any characters registered with me, I will be temporarily closing your user account. Please use ```!x add [char_name] [gsheet_link]``` to open another account if you so wish. ")

    cursor.close()
    db.close()

    # End of delete function

    return

  @commands.command( name = "erase", pass_context = True )
  @commands.is_owner()
  async def erase( self, ctx, arg ):

    message = ctx.message 

    await ctx.send( type(message.author.id) )
    await ctx.send( type(arg) )

    db = sqlite3.connect( USER_CHARS_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{int(arg)}' """)
    result = cursor.fetchone()

    if result is None:

      displayErrorMessage( self, ctx, ERASE_NO_CHAR_ERROR )
      cursor.close()
      db.close()
      return

    cursor.execute( f"""DELETE FROM user_chars WHERE user_id = '{int(arg)}'""")

    await ctx.send( "You have successfully deleted the specified account from my registry. Perhaps we may see them again?")

    cursor.close()
    db.close()

    # End of Erase Function 

    return

  # switchchar() function 
  # - allows users to switch which active character they are using 
  #   on the Xendros bot 
  @commands.command( name = "switchchar", pass_context = True , aliases = ["sc"])
  async def switchchar( self, ctx, arg = None ):

    # ERROR CASE: if command is not called correctly

    if arg is None: 
      displayErrorMessage( self, ctx, SWITCHCHAR_ARGS_LENGTH_ERROR )
      return

    message = ctx.message

    # Get character data from user_chars table 
    db = sqlite3.connect( USER_CHARS_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT active_char from user_chars WHERE user_id = '{message.author.id}' """ )
    
    
    result = cursor.fetchone()

    # ERROR CASE: If there is no data for the user
    if result is None:
      displayErrorMessage( self, ctx, USER_ID_NOT_FOUND_ERROR )
      cursor.close()
      db.close()
      return

    active_char = int( result[0] )

    # ERROR CASE: If the active character is already set 
    if active_char == arg:
      displayErrorMessage( self, ctx, SWITCHCHAR_ACTIVE_SET_ERROR )
      cursor.close()
      db.close()
      return

    # Get character ids from user_chars table 
  
    cursor.execute( f"""SELECT active_char, char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{message.author.id}'""" )
    result = cursor.fetchone()

    char_one_id = int( result[1] )
    char_two_id = int( result[2] )
    char_three_id = int( result[3] )

    # ERROR CASE: If only one character is registered
    if char_two_id == 0 and char_three_id == 0:

      displayErrorMessage( self, ctx, SWITCHCHAR_ONE_CHAR_ERROR )
      cursor.close()
      db.close()
      return

    # ERROR CASE: If slot chosen is not filled 
    if char_one_id == 0 and arg == 1:

      displayErrorMessage( self, ctx, SWITCHCHAR_CHAR_SLOT_ONE_ERROR )
      cursor.close()
      db.close()
      return

    elif char_two_id == 0 and arg == 2:

      displayErrorMessage( self, ctx, SWITCHCHAR_CHAR_SLOT_TWO_ERROR )
      cursor.close()
      db.close()
      return

    elif char_three_id == 0 and arg == 3:

      displayErrorMessage( self, ctx, SWITCHCHAR_CHAR_SLOT_THREE_ERROR )
      cursor.close()
      db.close()
      return

    # Set new active_char to user choice 
    sql = (""" UPDATE user_chars SET active_char = ? WHERE user_id = ? """)
    values = ( arg, message.author.id )
    cursor.execute( sql, values )
    db.commit()

    # Display successful switch of character to user 

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

    # End of switchchar() function

  # charlink function
  # - allows users to get google drive link to character at any point
  @commands.command( name = "charlink", pass_context = True )
  async def charlink( self, ctx ):

    message = ctx.message

    # Get current active character for user 
    db = sqlite3.connect( USER_CHARS_DATA_PATH )
    cursor = db.cursor()
    cursor.execute(f"""SELECT active_char, char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{ message.author.id }'""")

    result = cursor.fetchone()

    # ERROR CASE: If Result is None
    if result is None: 

      displayErrorMessage( self, ctx, USER_ID_NOT_FOUND_ERROR )
      cursor.close()
      db.close()
      return

    # Get Active Char ID 
    active_char = int( result[0] )

    if active_char == 1:
      char_id = int( result[1] )
    elif active_char == 2:
      char_id = int( result[2] )
    elif active_char == 3:
      char_id = int( result[3] )

    cursor.close()
    db.close()

    # Get Link for Character from char_data table 

    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor() 
    cursor.execute( f"SELECT user_id, char_name, drive_link FROM char_data WHERE char_id = '{char_id}'")
    result = cursor.fetchone() 

    # ERROR CASE: Character is not found in database
    if result is None:
      displayErrorMessage( self, ctx, CHAR_ID_NOT_FOUND_ERROR )
      cursor.close()
      db.close()
      return

    user_id = int( result[0] )
    char_name = str( result[1] )
    drive_link = str( result[2] )

    await ctx.send( f"Hello { char_name }! Here is the link to your character sheet (whatever that is...):")
    await ctx.send( f"{ drive_link }" )

    cursor.close()
    db.close()

  @commands.command( name = "charlist", pass_context = True , aliases = ["list"] )
  async def charlist( self, ctx ): 

    message = ctx.message

    db = sqlite3.connect( USER_CHARS_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{ message.author.id }'""")
    result = cursor.fetchone()

    # ERROR CASE: If result is none
    if result is None: 

      displayErrorMessage( self, ctx, USER_ID_NOT_FOUND_ERROR )
      cursor.close()
      db.close()
      return 

    char_one_id = int( result[0] )
    char_two_id = int( result[1] )
    char_three_id = int( result[2] )

    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()

    embed = discord.Embed(
      title = f"Characters for { message.author }",
      color = discord.Color.dark_blue()
    )

    if char_one_id != 0:
      cursor.execute( f"""SELECT char_name FROM char_data WHERE char_id = '{char_one_id}'""")
      result = cursor.fetchone()
      char_name = str( result[0] )
      embed.add_field( name = "Character Slot 1", 
                       value = f"{char_name} ({char_one_id})",
                       inline = False )
    elif char_one_id == 0:
      embed.add_field( name = "Character Slot 1", 
                       value = f"NONE",
                       inline = False )
    elif char_two_id != 0:
      cursor.execute( f"""SELECT char_name FROM char_data WHERE char_id = '{char_two_id}'""")
      result = cursor.fetchone()
      char_name = str( result[0] )
      embed.add_field( name = "Character Slot 2", 
                       value = f"{char_name} ({char_two_id})",
                       inline = False )
    elif char_two_id == 0:
      embed.add_field( name = "Character Slot 2", 
                       value = f"NONE",
                       inline = False )
    elif char_three_id != 0:
      cursor.execute( f"""SELECT char_name FROM char_data WHERE char_id = '{char_three_id}'""")
      result = cursor.fetchone()
      char_name = str( result[0] )
      embed.add_field( name = "Character Slot 3", 
                       value = f"{char_name} ({char_three_id})",
                       inline = False )
    elif char_three_id == 0:
      embed.add_field( name = "Character Slot 3", 
                       value = f"NONE",
                       inline = False )

    await ctx.send( embed = embed )

    # End of charlist() function 
    cursor.close()
    db.close()

    return 

  
  ## Money / Currency Functions 

  # balance function
  @commands.command( name = "balance", pass_context = True )
  async def balance( self, ctx ):

    message = ctx.message

    db = sqlite3.connect( USER_CHARS_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"SELECT active_char, char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{ message.author.id }'")

    result = cursor.fetchone()

    # ERROR CASE: If the player has not yet registered with the bot
    if result is None:

      await ctx.send( "Hmm, it seems it's your first time in my shop. Please register with me using ```!x add <character name> <gsheet link>```")
      cursor.close()
      db.close()
      return

    # Find Active Character
    active_char = int( result[0] )

    if active_char == 1:
      char_id = int( result[1] )
    elif active_char == 2:
      char_id = int( result[2] )
    elif active_char == 3:
      char_id = int( result[3] )


    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"SELECT user_id, drive_link, char_name, action_points, downtime, lore_tokens, platinum, electrum, gold, silver, copper, gacha_rolls FROM char_data WHERE char_id = '{char_id}'")
    result = cursor.fetchone()

    if result is None:
      await ctx.send( "Hmm, it seems it's your first time in my shop. Please register with me using ```!x add <character name> <gsheet link>```")
      cursor.close()
      db.close()
      return

    user_id = int( result[0] )
    drive_link = str( result[1] )
    char_name = str( result[2] )
    action_points = int( result[3] )
    downtime = int( result[4] )
    lore_tokens = int( result[5] )
    platinum = int( result[6] )
    electrum = int( result[7] )
    gold = int( result[8] )
    silver = int( result[9] )
    copper = int( result[10] )
    gacha_rolls = int( result[11] )

    # Create Embed for display

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
    embed.set_footer( text = f"User ID: {user_id}, Char ID: {char_id}")

    await ctx.send( embed = embed )    

    cursor.close()
    db.close() 

    # End of balance() function

  # deposit function 
  @commands.command( name = "deposit", pass_context = True )
  @commands.is_owner()
  async def deposit( self, ctx, *args ):

    # ERROR CASE: If # of arguments is not correct
    if len( args ) < 3:
      await ctx.send( "Unfortunately, you've messed up the command. Try running it this way:```!x deposit <char_id> <currency> <amount>")

    currency = CURRENCY_SWITCH.get( args[1], "NULL")

    # ERROR CASE: If input currency is invalid
    if currency == "NULL":

      await ctx.send("That is not a currency that I can currently track. Consider retyping the command with a valid currency")
      return

    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT { currency } FROM char_data WHERE char_id = '{args[0]}' """)
    result = cursor.fetchone()

    # ERROR CASE: If result is null 
    if result is None:

      await ctx.send( "Hmm, it seems I don't have that user on my list. Please have them register with me using ```!x add <char_name> <gsheet url>```")
      cursor.close()
      db.close()
      return

    current_amt = int( result[0])

    sql = ( f"""UPDATE char_data SET {currency} = ? WHERE char_id = ?""")
    values = ( current_amt + int(args[2]), int(args[0]) )
    cursor.execute( sql, values )
    db.commit()

    cursor.execute( f"""SELECT char_Name, {currency} FROM char_data WHERE char_id = '{args[0]}'""" )
    result = cursor.fetchone()

    char_name = str(result[0])
    new_amt = str(result[1])

    await ctx.send( f"Fantastic, I've deposited { args[2] } { args[1].upper() } into {char_name}'s account. Their new balance is {new_amt} { args[1].upper() } !")

    cursor.close() 
    db.close() 

    # End of deposit() function 

    return 

  # withdraw function
  @commands.command( name = "withdraw", pass_context = True )
  @commands.is_owner()
  async def withdraw( self, ctx, *args ):

    # ERROR CASE: If # of arguments is not correct
    if len( args ) < 3:
      await ctx.send( "Unfortunately, you've messed up the command. Try running it this way:```!x withdraw <char_id> <currency> <amount>")

    currency = CURRENCY_SWITCH.get( args[1], "NULL")

    if currency == "NULL":

      await ctx.send("That is not a currency that I can currently track. Consider retyping the command with a valid currency")
      return

    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT { currency } FROM char_data WHERE char_id = '{args[0]}' """)
    result = cursor.fetchone()

    if result is None:

      await ctx.send( "Hmm, it seems I don't have that user on my list. Please have them register with me using ```!x add <char_name> <gsheet url>```")
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
  @commands.command( name = "setbal", pass_context = True )
  async def setbal( self, ctx, *args ):

    # ERROR CASE: If # of arguments is not correct
    if len( args ) < 3:
      await ctx.send( "Unfortunately, you've messed up the command. Try running it this way:```!x withdraw <char_id> <currency> <amount>")

    currency = CURRENCY_SWITCH.get( args[1], "NULL")

    if currency == "NULL":

      await ctx.send("That is not a currency that I can currently track. Consider retyping the command with a valid currency")
      return

    db = sqlite3.connect( CHAR_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT { currency } FROM char_data WHERE char_id = '{args[0]}' """)
    result = cursor.fetchone()

    if result is None:

      await ctx.send( "Hmm, it seems I don't have that user on my list. Please have them register with me using ```!x add <char_name> <gsheet url>```")
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

    # TODO: complete currex function
    # EX USAGE: !x currex <currency_one> <currency_two>

    # ERROR CASE: if # of args is incorrect
    if len( args ) < 2:

      return 

    message = ctx.message

    # Get user char data 
    db = sqlite3.connect( USER_CHARS_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT active_char, char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{ message.author.id }'""")
    result = cursor.fetchone()

    # ERROR CASE: If user is not registered
    if result is None:

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

    currency_one = CURRENCY_SWITCH.get( args[0], "NULL")
    currency_two = CURRENCY_SWITCH.get( args[1], "NULL")

    # ERROR CASE: If input currency is invalid
    if currency_one == "NULL" or currency_two == "NULL":

      await ctx.send("That is not a currency that I can currently track. Consider retyping the command with a valid currency")
      cursor.close()
      db.close()
      return
    # ERROR CASE: If downtime is attempted for conversion
    elif currency_one == "downtime" or currency_two == "downtime":
      await ctx.send("I cannot convert downtime into money, unfortunately. Consider retyping the command with a valid currency")
      cursor.close()
      db.close()
      return
    # ERROR CASE: If ap / lt and pp/ep/gp/sp/cp are being converted between.
    elif (currency_one == "action_points" or currency_one == "lore_tokens") and (currency_two == "platinum" or currency_two == "gold" or currency_two == "silver" or currency_two == "copper" or currency_two == "electrum"):
      await ctx.send("I cannot convert AP / LT into money, or vice versa. Consider retyping the command with a valid currency")
      cursor.close()
      db.close()
      return
    elif (currency_two == "action_points" or currency_two == "lore_tokens") and (currency_one == "platinum" or currency_one == "gold" or currency_one == "silver" or currency_one == "copper" or currency_one == "electrum"):
      await ctx.send("I cannot convert AP / LT into money, or vice versa. Consider retyping the command with a valid currency")
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

      cursor.close()
      db.close()
      return

    # Check amt of first currency
    curr_one_amt = int( result[0] )
    curr_two_amt = int( result[0] )

    conversion_chart = {
      "action_points": 5,
      "lore_tokens": 0.2,
      "platinum": 0.1,
      "electrum": 0.5,
      "gold": 1,
      "silver": 10,
      "copper": 100
    }

    curr_one_conversion = conversion_chart.get( currency_one, "NULL" )
    curr_two_conversion = conversion_chart.get( currency_two, "NULL" )

    # ERROR CASE: If amt cannot be converted

    # Convert currency_one to currency_two
    if curr_one_conversion == curr_two_conversion:

      return

    elif curr_one_conversion < curr_two_conversion:

      new_curr_one_amt = curr_one_amt % curr_one_conversion
      new_curr_two_amt = curr_one_amt * curr_one_conversion

    elif curr_one_conversion > curr_two_conversion:

      new_curr_two_amt = floor(curr_one_amt / curr_one_conversion)
      new_curr_one_amt = curr_one_amt % curr_one_conversion

    # Update character data 

  
  ## Gacharoll Functions

  @commands.group( name = "gacharoll", pass_context = True, aliases = ["gr"] )
  async def gacharoll( self, ctx ):

    if ctx.invoked_subcommand is None:

      await ctx.send( "Invalid subcommand passed..." )

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

      return

    gold = int( result[0] )
    gacha_rolls = int( result[1] )

    # ERROR CASE: Not enough money to roll
    if gold < UC_ROLL_COST:

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

    gold = int( result[0] )
    gacha_rolls = int( result[1] )

    # ERROR CASE: Not enough money to roll
    if gold < R_ROLL_COST:

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
  @commands.group( name = "gachaadmin", pass_context = True , aliases = ["ga"])
  @commands.is_owner()
  async def gachaadmin( self, ctx ):

    if ctx.invoked_subcommand is None:

      await ctx.send( "Invalid subcommand passed..." )

  # rollUncommon_admin

  # rollRare_admin

  # rollVeryRare_admin
  
  # rollLegendary_admin


# End Xendros Cog

def setup( bot ):
  bot.add_cog( XendrosCog( bot ) )
  print( '------\nXendros Cog has been loaded!\n------')