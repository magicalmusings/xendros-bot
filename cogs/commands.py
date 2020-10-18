from __future__ import print_function

import discord
from discord.ext import commands
import sys

HELP_LINK = "https://magicalmusings.github.io/xendros-bot/"

class Commands( commands.Cog ):

  def __init__(self, bot ):
    self.bot = bot
    

  @commands.Cog.listener()
  async def on_ready( self ):
    print( "------\nCommands Cog has been loaded!\n------" )

  """
  =================================================================================
                                BOT COMMAND DEFINITIONS
  =================================================================================
  """

  # HELP COMMAND
  @commands.command( name = "help", pass_context = True )
  async def help( self, ctx ):

    await ctx.send("Looks like you need some help getting around. Take a look at this link for how to use my powers to your benefit.")
    await ctx.send( HELP_LINK )

    return


  # PING COMMAND
  @commands.command( name = "ping", pass_context = True )
  async def _ping( self, ctx ):
    """
      Diagnostic command to check latency on Bot Commands
    """
    await ctx.send( "Pong! The crows took {0}ms in reaching you...".format(
      round( self.bot.latency * 1000, 1 ) ) )

  # STATS COMMAND
  @commands.command( name = "stats" , pass_context = True )
  async def _stats( self, ctx ):
    """
      Diagnostic command to check version of python and discord.py
    """
    pythonVersion = sys.version
    dpyVersion = discord.__version__
    await ctx.send( f"I'm running on Python {pythonVersion} and discord.py {dpyVersion}! Whatever that means." )

# End of Commands Cog Definition 

def setup( bot ):
  bot.add_cog( Commands( bot ) )

  

  

  