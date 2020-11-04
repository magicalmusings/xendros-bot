import discord
from discord.ext import commands

import cogs.xendros as xendros
import cogs.error_display as error_display
from cogs.error_display import ERROR_CODES

## Dice Rolling Functions 
# TODO: implement skill check rolls
# TODO: implement saving throw rolls
# TODO: implement dice rolling in general
#   > TODO: allow users to roll via "1d20", "2d4 +4", etc.
#   > TODO: allow multiple dice rolls at once via "(1d20 +6) (1d4)"
# TODO: integrate character sheets with kallista to track stats for rolls
#   > TODO: get new google drive API key
#   > TODO: update JSON to include stats for skill checks / saving throws 
#   > TODO: implement update function to call when:
#     >> TODO: update individual stats when adding a new character
#     >> TODO: when Xendros first boots up
#     >> TODO: when !x update is called

class XendrosDiceRollingCog ( commands.Cog, name = "XendrosDiceRolling "):

  def __init__(self, bot):

    self.bot = bot

    return

  # End of DiceRollingCog

def setup( bot ):
  bot.add_cog( XendrosDiceRollingCog( bot ) )
  print( "DicerollingCog loaded!")