from __future__ import print_function

import os

from discord.ext import commands # pylint: disable=import-error
from flask import Flask # pylint: disable=import-error
from threading import Thread

# Initialize Flask app for use with bot
app = Flask( 'discord bot' )

# Set what is written on xendros-bot--andresgsepulved.repl.co
@app.route( '/' )
def hello_world():
    return 'Magic Appetizers not included.'

# Start server on 0.9.0.0:8080
def start_server():
  app.run( host='0.0.0.0',port=8080 )
  
# Start Flask Thread for sustaining bot over time
t = Thread( target=start_server )
t.start()

# Set prefix of bot
bot = commands.Bot( 
  command_prefix = '!x ',
  case_insensitive = True,
  owner_id = 197158011469299713 )
bot.remove_command("help")

# Pull secret token from .env file
token =  os.environ.get( "DISCORD_BOT_SECRET" )
bot.config_token = token

# Import all commands and events from cogs folder
if __name__ == '__main__':

  for file in os.listdir( "cogs" ):

    if file.endswith( ".py" ) and not file.startswith( "_" ) and not file.startswith("error"):
      bot.load_extension( f"cogs.{file[:-3]}" )

  for file in os.listdir( "cogs/modules"):

    if file.endswith( ".py" ) and not file.startswith( "_" ):
      bot.load_extension( f"cogs.modules.{file[:-3]}" )

      
  # Run the Bot
  bot.run( bot.config_token )

