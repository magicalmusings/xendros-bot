from copy import copy
import discord # pylint: disable=import-error
from discord.ext import commands # pylint: disable=import-error
import math

import cogs.xendros as xendros
import cogs.error_display as error_display
from cogs.error_display import ERROR_CODES

## Shopkeeping Functions To Do List
  # TODO: Implement Shops of Different Kinds
  # TODO: Implement Buying / Selling of Items
  # TODO: Implement buyback of items

class XendrosShopkeepingCog( commands.Cog, name = "XendrosShopkeeping" ):

    def __init__( self, bot ):

        self.bot = bot

        self.CURRENCY_SWITCH = {
            'ap': "action_points",
            'cp': "copper",
            'dt': "downtime",
            'ep': "electrum",
            'gp': "gold",
            'lt': "lore_tokens",
            'pp': "platinum",
            'sp': 'silver'
        }

        self.CONVERSION_CHART = {
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

        print( "Shopkeeping initialization complete!")

        return

    ## Money / Currency Functions 

    async def displayBalanceEmbed( self, ctx, user_data ):

        message = ctx.message 

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
            await error_display.displayErrorMessage( ctx, ERROR_CODES.BALANCE_URL_ERROR )
            return

        await ctx.send( embed = embed )    

        return

    # balance function
    @commands.command( name = "balance", pass_context = True , aliases = ['bal'])
    async def balance( self, ctx ):

        await self.bot.wait_until_ready()

        message = ctx.message

        char_data = await xendros.getCharData()

        # ERROR CASE: If the player has not yet registered with the bot
        if str(message.author.id) not in char_data:
            await error_display.displayErrorMessage( ctx, ERROR_CODES.USER_ID_NOT_FOUND_ERROR )
            return

        # Find Active Character
        user_data = char_data[str(message.author.id)]

        await self.displayBalanceEmbed( ctx, user_data )

        return

        # End of balance() function

    async def getKeyPath( self, results, path, d, target ):

        for key, value in d.items():

            path.append(key)
            if isinstance( value, dict ):
                await self.getKeyPath( results, path, value, target )
            if value == target:
                results.append( copy(path) )
            path.pop()
        
        return
        # End of getKeyPath() function

    async def getUserIDFromName( self, char_name ):

        char_data = {}
        char_data_keys = []
        path = []

        char_data = await xendros.getCharData()

        await self.getKeyPath(char_data_keys, path, char_data, char_name)

        user_id = char_data_keys[0][0]

        return user_id

        # End of getUserIDFromName() function
    
    # deposit function 
    @commands.command( name = "deposit", pass_context = True , aliases = ['dep'])
    @commands.is_owner()
    async def deposit( self, ctx, *args ):

        await self.bot.wait_until_ready()

        # ERROR CASE: If # of arguments is not correct
        if len( args ) < 3:
            await error_display.displayErrorMessage( ctx, ERROR_CODES.DEPOSIT_ARGS_LENGTH_ERROR )
            return

        char_data = {}
        currency = self.CURRENCY_SWITCH.get( args[1], "NULL")

        # print( currency )

        # ERROR CASE: If input currency is invalid
        if currency == "NULL":

            await error_display.displayErrorMessage( ctx, ERROR_CODES.DEPOSIT_CURRENCY_ERROR )
            return

        # ERROR CASE: If result is null 
        try:
            # print( args[0] )
            char_data = await xendros.getCharData()
            user_id = await self.getUserIDFromName( args[0] )
            user_data = char_data[ user_id ]
            active_char_slot = user_data["active_char"]
            active_char = user_data[active_char_slot]
            # print( active_char )
        except:
            await error_display.displayErrorMessage( ctx, ERROR_CODES.CHAR_ID_NOT_FOUND_ERROR )
            return
        
        current_amt = int( active_char.get(currency) )

        active_char[currency] = str( current_amt + int( args[2] ) )

        char_name = str(active_char["char_name"])
        new_amt = str(active_char[currency])

        await ctx.send( f"Fantastic, I've deposited { args[2] } { args[1].upper() } into {char_name}'s account. Their new balance is {new_amt} { args[1].upper() } !")

        await xendros.updateCharData( char_data )

        return 

        # End of deposit() function 

    # withdraw function
    @commands.command( name = "withdraw", pass_context = True )
    @commands.is_owner()
    async def withdraw( self, ctx, *args ):

        await self.bot.wait_until_ready()

        # ERROR CASE: If # of arguments is not correct
        if len( args ) < 3:
            await error_display.displayErrorMessage( ctx, ERROR_CODES.WITHDRAW_ARGS_LENGTH_ERROR )
            return

        currency = self.CURRENCY_SWITCH.get( args[1], "NULL")

        if currency == "NULL":
            await error_display.displayErrorMessage( ctx, ERROR_CODES.WITHDRAW_CURRENCY_ERROR )
            return

        try:
            # print( args[0] )
            char_data = await xendros.getCharData()
            user_id = await self.getUserIDFromName( args[0] )
            user_data = char_data[ user_id ]
            active_char_slot = user_data["active_char"]
            active_char = user_data[active_char_slot]
            # print( char_data )
        except:
            await error_display.displayErrorMessage( ctx, ERROR_CODES.CHAR_ID_NOT_FOUND_ERROR )
            return 

        current_amt = int( active_char.get( currency ) )

        calc = current_amt - int( args[2] )
        if calc < 0:
            calc = 0

        active_char[currency] = str( calc )

        char_name = str( active_char["char_name"] )
        new_amt = str( active_char[currency] )

        await ctx.send( f"I've withdrawn { args[2] } { args[1].upper() } from {char_name}'s account. Their new balance is {new_amt} { args[1].upper() } !")

        await xendros.updateCharData( char_data )

        # End of withdraw() function
        return

    # setbal function
    @commands.command( name = "setbal", pass_context = True , aliases = ['sb'])
    @commands.is_owner()
    async def setbal( self, ctx, *args ):

        await self.bot.wait_until_ready()

        # ERROR CASE: If # of arguments is not correct
        if len( args ) < 3:
            await error_display.displayErrorMessage( ctx, ERROR_CODES.SETBAL_ARGS_LENGTH_ERROR )
            return

        currency = self.CURRENCY_SWITCH.get( args[1], "NULL")

        if currency == "NULL":
            await error_display.displayErrorMessage( ctx, ERROR_CODES.SETBAL_CURRENCY_ERROR )
            return

        try:
            # print( args[0] )
            char_data = await xendros.getCharData()
            user_id = await self.getUserIDFromName( args[0] )
            user_data = char_data[ user_id ]
            active_char_slot = user_data["active_char"]
            active_char = user_data[active_char_slot]
            # print( char_data )
        except:
            await error_display.displayErrorMessage( ctx, ERROR_CODES.CHAR_ID_NOT_FOUND_ERROR )
            return 

        new_amt = int(args[2])
        if new_amt < 0:
            new_amt = 0

        current_amt = active_char[currency]
        active_char[currency] = str(new_amt)

        char_name = active_char["char_name"]
        new_amt = str( active_char[currency] )

        await ctx.send( f"Great, I've set {char_name}'s {currency.upper()} amount from {current_amt} {args[1].upper()} to { new_amt} { args[1].upper() } !")

        await xendros.updateCharData( char_data )

        return 

        # End of setbal() function

    # currex function
    @commands.command( name = "currex", pass_context = True, aliases = ["cx"] )
    async def currex( self, ctx, *args ):

        # EX USAGE: !x currex <currency_one> <currency_two>

        await self.bot.wait_until_ready()

        # ERROR CASE: if # of args is incorrect
        if len( args ) < 3:
            await error_display.displayErrorMessage( ctx, ERROR_CODES.CURREX_ARGS_LENGTH_ERROR )
            return 

        message = ctx.message

        # Get user char data 
        char_data = await xendros.getCharData()

        # ERROR CASE: If user is not registered
        if str( message.author.id) not in char_data:
            await error_display.displayErrorMessage( ctx, ERROR_CODES.USER_ID_NOT_FOUND_ERROR )
            return

        user_data = char_data[str(message.author.id)]
        active_char_slot = user_data["active_char"]
        active_char = user_data[active_char_slot]

        amt_to_convert = int( args[0] )
        currency_one = self.CURRENCY_SWITCH.get( args[1], "NULL")
        currency_two = self.CURRENCY_SWITCH.get( args[2], "NULL")

        # ERROR CASE: If input currency is invalid
        if currency_one == "NULL" or currency_two == "NULL":
            await error_display.displayErrorMessage( ctx, ERROR_CODES.CURREX_INVALID_CURRENCY_ERROR )
            return

        # ERROR CASE: If downtime is attempted for conversion
        elif currency_one == "downtime" or currency_two == "downtime":
            await error_display.displayErrorMessage( ctx, ERROR_CODES.CURREX_DOWNTIME_INPUT_ERROR )
            return

        elif currency_one == "action_points" or currency_one == "lore_tokens" or currency_two == "action_points" or currency_two == "lore_tokens":
            await error_display.displayErrorMessage( ctx, ERROR_CODES.CURREX_AP_LT_CONVERSION_ERROR )
            return

        # ERROR CASE: If ap / lt and pp/ep/gp/sp/cp are being converted between.
        elif (currency_one == "action_points" or currency_one == "lore_tokens") and (currency_two == "platinum" or currency_two == "gold" or currency_two == "silver" or currency_two == "copper" or currency_two == "electrum"):
            await error_display.displayErrorMessage( ctx, ERROR_CODES.CURREX_INVALID_CONVERSION_ERROR )
            return

        elif (currency_two == "action_points" or currency_two == "lore_tokens") and (currency_one == "platinum" or currency_one == "gold" or currency_one == "silver" or currency_one == "copper" or currency_one == "electrum"):
            await error_display.displayErrorMessage( ctx, ERROR_CODES.CURREX_INVALID_CONVERSION_ERROR )
            return

        # Check current balance

        # Check amt of first currency
        curr_one_amt = int( active_char[currency_one] )

        # ERROR CASE: if we don't have enough currency in order to make it work
        if curr_one_amt == 0:
            await error_display.displayErrorMessage( ctx, ERROR_CODES.CURREX_NOT_ENOUGH_CURRENCY_ERROR )
            return 

        # If we don't have enough currency, but still have currency:
        #  - use what's left to convert. 
        if curr_one_amt - amt_to_convert < 0:
            await ctx.send( f"Oops, looks like you don't have all the currency to convert. I'll just use the **{curr_one_amt}** {currency_one} that's left in your account." )
            amt_to_convert = curr_one_amt

        curr_two_amt = int( active_char[currency_two] )

        conversion_rate = self.CONVERSION_CHART[currency_one][currency_two]
        backwards_conversion_rate = self.CONVERSION_CHART[currency_two][currency_one]

        # ERROR CASE: Converting between the same currency
        if conversion_rate == 1 or backwards_conversion_rate == 1:
            await error_display.displayErrorMessage( ctx, ERROR_CODES.CURREX_NO_CONVERSION_NEEDED_ERROR )
            return
        
        # Examples of conversion are included below. For the purposes of examples, lets say the user currently has: 
        # - curr_one_amt = 12 pp
        # - curr_two_amt = 100 gp

        # Calculate amt of currency to add to currency_two
        # Ex: for 12 pp -> gp , 12pp x 10 (pp->gp conversion rate) = 120 gp to add
        curr_to_add = math.floor( amt_to_convert * conversion_rate )

        # ERROR CASE: 
        if curr_to_add <= 0:
            await error_display.displayErrorMessage( ctx, ERROR_CODES.CURREX_NOT_ENOUGH_CURRENCY_ERROR )
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
        active_char[currency_one] = str(new_curr_one_amt)
        active_char[currency_two] = str(new_curr_two_amt)

        # Display conversion success and balance to user
        await ctx.send( f"Success! I've converted your **{amt_to_convert}** {currency_one} into **{curr_to_add}** {currency_two}!! Your new balance is: ")
        
        await xendros.updateCharData( char_data )

        await self.balance( ctx )

        # End of currex function
        return

    # End of XendrosShopkeepingCog class

def setup( bot ):
    bot.add_cog( XendrosShopkeepingCog( bot ) )
    print( '------\nShopkeeping Cog has been loaded!\n------' )