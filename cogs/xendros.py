import discord
from discord.ext import commands
import disputils
import json
from jsonmerge import merge
import sqlite3

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
RARE_ITEMS = {}
RARE_ITEMS_PATH = "data/rare.json"
READ_TAG = "r"
UNCOMMON_ITEMS = {}
UNCOMMON_ITEMS_PATH = "data/uncommon.json"
USER_CHARS_DATA_PATH = "data/user_chars.sqlite"
WRITE_TAG = "w"

class XendrosCog( commands.Cog, name = "Xendros" ):

  def __init__( self, bot ):

    self.bot = bot

    # Import Magic Item Data

    with open( UNCOMMON_ITEMS_PATH, READ_TAG ) as read_file:
      UNCOMMON_ITEMS = json.load( read_file )

    with open( RARE_ITEMS_PATH, READ_TAG ) as read_file:
      RARE_ITEMS = json.load( read_file )

    print( f'Loaded {len(UNCOMMON_ITEMS['uncommon'])} uncommon magic items!' )
    print( f'Loaded {len(RARE_ITEMS['uncommon'])} rare magic items!' )

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

  # add() function
  # - adds a character to the database
  @commands.command( name = "add", pass_context = True )
  async def add( self, ctx, *args ):

    # ERROR CASE(S): If command is given improperly 
    if args is None or len( args ) < 2:
      await ctx.send( "I need a name and url for tracking inventory, darling. Try running the command again like this: ```!x add <char_name> <gsheet url> ```")
      return

    char_add_flag = False
    message = ctx.message
    
    # Grab current information from user_chars table 

    db = sqlite3.connect( USER_CHARS_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( 
      f"SELECT user_id, char_one_id, char_two_id, char_three_id FROM user_chars WHERE user_id = '{ message.author.id }'")

    result = cursor.fetchone()

    # ERROR CASE: If this is the users first time using Kallista
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
      await ctx.send( "Darling, you already have three characters registered with me. How many more do you need? Consider deleting one using ```!x delete <char_number>```" )
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

      await ctx.send( "Alas darling, you must tell me which character you'd like to delete to. Try using the command like this: ```!x delete <char_slot>```")
      return

     # Get Character ID
    char_slot = int( arg )

    char_one_id = int( result[0] )
    if char_one_id == 0 and char_slot == 1:

      await ctx.send( "Unfortunately, I cannot delete that which does not exist. That character slot is currently empty in my books.")
      cursor.close()
      db.close()
      return

    char_two_id = int( result[1] )
    if char_two_id == 0 and char_slot == 2:

      await ctx.send( "Unfortunately, I cannot delete that which does not exist. That character slot is currently empty in my books.")
      cursor.close()
      db.close()
      return

    char_three_id = int( result[2] )
    # ERROR CASE: If the specified slot is already empty
    if char_three_id == 0 and char_slot == 3:

      await ctx.send( "Unfortunately, I cannot delete that which does not exist. That character slot is currently empty in my books.")
      cursor.close()
      db.close()
      return

    
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

      await ctx.send( "Unfortunately, I cannot erase that which does not exist. That user  is not currently registered in my books.")
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
      await ctx.send( "Alas darling, you must tell me which character you'd like to switch to. Try using the command like this: ```!x switchchar <char_slot>```")
      return

    message = ctx.message

    # Get character data from user_chars table 
    db = sqlite3.connect( USER_CHARS_DATA_PATH )
    cursor = db.cursor()
    cursor.execute( f"""SELECT active_char from user_chars WHERE user_id = '{message.author.id}' """ )
    
    
    result = cursor.fetchone()

    # ERROR CASE: If there is no data for the user
    if result is None:
      await ctx.send( "I don't seem to have any characters registered with you. Please attempt to add a character using ```!x add <gsheet_url>```")
      cursor.close()
      db.close()
      return

    active_char = int( result[0] )

    # ERROR CASE: If the active character is already set 
    if active_char == arg:

      await ctx.send( f"I have already set your active character to Character Slot {arg}. No need to tell me twice!")
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

      await ctx.send( "You only have one character registered with me, love. Consider adding another using ```!x add <gsheet url>```")
      cursor.close()
      db.close()
      return

    # ERROR CASE: If slot chosen is not filled 
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

      await ctx.send( "Hmm, it seems it's your first time in my shop. Please register with me using ```!x add <character name> <gsheet_url>```")
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

      await ctx.send( "Hmm, it seems it's your first time in my shop. Please register with me using ```!x add <character name> <gsheet_url>```")
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

  ## Gacharoll Functions

  @commands.group( name = "gacharoll", pass_context = True )
  async def gacharoll( self, ctx ):

    if ctx.invoked_subcommand is None:

      await ctx.send( "Invalid subcommand passed..." )

  # rollUncommon function
  @gacharoll.command( name = "uncommon", pass_context = True, aliases = ["UC"])
  async def rollUncommon( self, ctx, arg = None ):

    # TODO: Implement rollUncommon()

    return 

  # rollRare function  

  # rollVeryRare function  

  # rollLegendary function
  

# End Xendros Cog

def setup( bot ):
  bot.add_cog( XendrosCog( bot ) )
  print( '------\nXendros Cog has been loaded!\n------')