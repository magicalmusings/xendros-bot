import discord # pylint: disable=import-error
import enum

from discord.ext import commands #pylint: disable=import-error

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
  ROLLCOMMAND_SUBCOMMAND_ERROR = 31

class XendrosErrorHandlingCog( commands.Cog, name = "XendrosErrorHandling"):

    def __init__( self, bot ):

        self.bot = bot

        self.error_messages = {}

        await self.loadErrorMessages()

        print( "Error Handling Cog Initialization Complete!" )

        return 

    async def loadErrorMessages( self ):

        self.error_messages = {
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
            ERROR_CODES.ROLLCOMMAND_SUBCOMMAND_ERROR: "Invalid subcommand passed... please try using the command like !x roll <parameter>",
            }

        return 

        # End of LoadErrorMessage() function
        
    async def displayErrorMessage( self, ctx, error_code ):

        await self.bot.wait_until_ready()

        error_msg_str = self.error_messages.get( error_code, "CODE NOT FOUND" )

        if error_msg_str == "CODE NOT FOUND":
            print( "ERROR CODE NOT FOUND, RETURNING EMPTY STRING")
            error_msg_str = ""

        await ctx.send( error_msg_str )

        return

        # end of displayErrorMessage() function 

def setup( bot ):
    bot.add_cog( XendrosErrorHandlingCog( bot ) )
    print( '------\nError Handling Cog has been loaded!\n------')