
import discord
from discord.ext import commands
import json
from jsonmerge import merge
import sqlite3

EMPTY_JSON = '{}'
READ_TAG = 'r'
WRITE_TAG = 'w'

class Events( commands.Cog ):

  def __init__( self, bot ):
    self.bot = bot
  """
  =================================================================================
                                BOT EVENT DEFINITIONS
  =================================================================================
  """

  @commands.Cog.listener()
  async def on_ready( self ):
    """
      On Ready; When the bot is successfully booted up.
    """

    # Changes bot presence on Discord
    await self.bot.change_presence( 
      activity=discord.Activity( 
        type = discord.ActivityType.watching, name = "your wallet | !x help"
      ) )
    # Console Output to show bot is working
    print( '------\nLogged in as' )
    print( self.bot.user.name )
    print( self.bot.user.id )
    print( 'https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=0'.format('707346305080361022' ) )
    print( '------' )

  @commands.Cog.listener()
  async def on_command_error( self, ctx, error ):
    """
      Handles command errors from the bot that do not include
      the errors in the ignored list
    """
    ignored = (
      commands.CommandNotFound,
      commands.UserInputError
    )

    # if the command error is one we ignore, return
    if isinstance( error, ignored ):
      return

    # Begin error handling

    # Cooldown checks
    if ( isinstance( error, commands.CommandOnCooldown ) ):

      # Math for determining cooldown in seconds, minutes, and hours
      m, s = divmod( error.retry_after, 60)
      h, m = divmod( m, 60 )

      # Handling if there is a cooldown seconds long
      if( int(h) == 0 and int(m) == 0 ):
        await ctx.send( f"Alas, you must wait {int(s)} to utilize this command again." )
      # Checking if cooldown is minutes long
      elif ( int (h) == 0 and int(m) != 0 ):
        await ctx.send( f"Alas, you must wait {int(m)} minutes and {int(s)} seconds to utilize this command again." )
      # Assuming cooldown is hours long
      else:
        await ctx.send( f"Alas, you must wait {int(h)} hours, {int(m)} minutes, and {int(s)} seconds to utilize this command again.")

    # Permissions Check Failures
    elif( isinstance( error, commands.CheckFailure ) ):
      await ctx.send( "It seems you're not a high enough level to command me. Pitiful!" )

    # Raise error up to console
    raise error

  @commands.Cog.listener()
  async def on_message( self, message ):
    """
      On Message; Defines behavior for bot depending on message send in chats it has access to
    """
    # Ignore the bots own commands, or it'll break
    if message.author.id == self.bot.user.id:
      return

# End of Events Cog Definition

def setup( bot ):
  bot.add_cog( Events( bot ) )