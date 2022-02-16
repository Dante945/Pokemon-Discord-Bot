import os
import discord
import requests
import json
import random
from keep_alive import keep_alive
from discord.ext import commands
import asyncio

cooldown = {}  # Tracks users each time they spawn a pokemon to put them on a cooldown
current_channels = ['general', 'bot-speak', 'sorryboutit', 'peepy-prison']  # Whitelisted channel names
# PokeBot, OWO , Ramen, Purity, Dyno, Hydra
bots = [894124882282033152, 408785106942164992, 723174588992716881, 486970979290054676, 155149108183695360,
        547905866255433758]  # Blacklisted bots to avoid spam spawning

# Help Card
def create_help_embed():
    embed = discord.Embed(
        title="Welcome to the Pokemon Discord Bot!",
        description="A wild pokemon will spawn every so often\nGuess it's name to catch it",
        colour=discord.Colour.red()
    )
    embed.add_field(name="Command : '%dex'", value='Displays you current dex', inline=True)
    return embed

# Caught a Pokemon Card
def create_caught_embed(pokemon_name):
    embed = discord.Embed(
        title="Correct!",
        description=f'You caught a {pokemon_name}',
        colour=discord.Colour.red()
    )
    return embed

# Wild Pokemon Card
def create_wild_embed(pokemon):
    pokemon_sprite = pokemon['Sprite']
    embed = discord.Embed(
        colour=discord.Colour.red()
    )
    embed.set_footer(text="Who's That Pokemon!")
    embed.set_image(url=pokemon_sprite)
    embed.set_author(name="A wild Pokemon Appeared!",
                     icon_url="https://pbs.twimg.com/profile_images/1347869339052072963/oA0oMpur_400x400.jpg")
    return embed

# Pokemon Information Card
def create_info_embed(pokemon):
    embed = discord.Embed(
        colour=discord.Colour.red()
    )
    embed.set_image(url=f"https://play.pokemonshowdown.com/sprites/ani/{pokemon['Name']}.gif")
    embed.set_author(name=f"{pokemon['Name'].title()}",
                     icon_url="https://pbs.twimg.com/profile_images/1347869339052072963/oA0oMpur_400x400.jpg")

    info, stats = stylize_output(pokemon)
    embed.add_field(name="Info", value=info, inline=True)
    return embed

def stylize_output(pokemon):
    # Formatting the pokemon's data for a cleaner look when used within the embeds
    information_box = ""
    information_box += f"Level: {pokemon['Level']}\n"

    if len(pokemon['Type']) > 1:
        information_box += f"Type: {pokemon['Type'][0].title()}/{pokemon['Type'][1].title()}\n"
    else:
        information_box += f"Type: {pokemon['Type'][0].title()}\n"
    information_box += f"Ability: {pokemon['Ability'].title()}"

    stats_box = f"Hp: {pokemon['Stats']['Hp']}\nAttack: {pokemon['Stats']['AtK']}\nSpecial Attack: {pokemon['Stats']['SpA']}\nDefense: {pokemon['Stats']['Def']}\nSpecial Defense: {pokemon['Stats']['SpD']}\nSpeed: {pokemon['Stats']['Spe']}"

    return information_box, stats_box

def initialize_pokemon():
    # Calls a pokemon API to retrieve the info on a random pokemon
    pokemon_number = random.randint(1, 898)
    response = requests.get(url=f"https://pokeapi.co/api/v2/pokemon/{pokemon_number}")
    pokemon_json = response.json()

    # Information gathering by parsing the json output
    pokemon_name = pokemon_json["forms"][0]['name']

    pokemon_abilities = pokemon_json['abilities']
    ability = random.choice(pokemon_abilities)['ability']['name']

    types = []
    pokemon_types = pokemon_json['types']
    for type in pokemon_types:
        types.append(type['type']['name'])

    stats = []
    pokemon_stats = pokemon_json['stats']
    for stat in pokemon_stats:
        stats.append(stat['base_stat'])

    # Randomization of Levels and Shiny
    level = random.randint(1, 100)
    if random.randint(1, 4096) == 1:
        sprite_link = f"https://play.pokemonshowdown.com/sprites/ani-shiny/{pokemon_name}.gif"
    else:
        sprite_link = f"https://play.pokemonshowdown.com/sprites/ani/{pokemon_name}.gif"

    # General Format of Pokemon
    pokemon = {
        "Name": pokemon_name,
        "Level": level,
        "Type": types,
        "Ability": ability,
        "Stats": {
            "Hp": stats[0],
            "AtK": stats[1],
            "SpA": stats[2],
            "SpD": stats[3],
            "Def": stats[4],
            "Spe": stats[5],
        },
        "Sprite": sprite_link
    }
    return pokemon

async def test(ctx, arg):
    await ctx.send(arg)

PokeBot = commands.Bot(command_prefix="%")

@PokeBot.event
async def on_ready():
    print('Logged in as {0.user}'.format(PokeBot))

@PokeBot.command()
async def bot(ctx):
    await ctx.channel.send(embed=create_help_embed())

@PokeBot.command()
async def dex(ctx):
    user = ctx.author.id
    new_pokemon = {user: []}

    # Try to open the json file to load its data, if empty: initialize
    try:
        with open("pokemon_storage.json", "r") as data_file:
            data = json.load(data_file)
    except json.decoder.JSONDecodeError:
        with open("pokemon_storage.json", "w") as data_file:
            json.dump(new_pokemon, data_file)

    with open("pokemon_storage.json", "r") as data_file:
        data = json.load(data_file)
    # Validates that the user has caught any pokemon yet
    if str(user) in data and len(data[str(user)]) > 0:
        user_data = data[str(user)]
        dex_list = []
        for entry in user_data:  # Iteratively grabs all pokemon from users dex
            pokemon = json.loads(entry)
            dex_list.append(pokemon)
        embeded_pages = []
        for pkm in dex_list:  # Iteratively creates a unique embed per pokemon to display
            embeded_pages.append(create_info_embed(pkm))  #

        PokeBot.help_pages = embeded_pages
        buttons = [u"\u23EA", u"\u2B05", u"\u27A1", u"\u23E9"]  # Emoji which act as buttons
        curr_page = 0
        msg = await ctx.channel.send(embed=PokeBot.help_pages[curr_page])
        for button in buttons:
            await msg.add_reaction(button)

        # Navigation is done through the reactions
        # Constantly Checks whether or not the user has switched pages by adding a reaction
        # Depending on the reaction, it will move through the different embeds representing a users dex
        # Once a reactions is added, it will switch pages and remove all current reactions
        # If nothing happens for 60 seconds, it will delete the message and embed
        while True:
            try:
                reaction, user = await PokeBot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)

            except asyncio.TimeoutError:
                await msg.delete()
                await ctx.message.delete()
                return print("test")

            else:
                previous_page = curr_page
                if reaction.emoji == u"\u23EA":
                    curr_page = 0

                elif reaction.emoji == u"\u2B05":
                    if curr_page > 0:
                        curr_page -= 1

                elif reaction.emoji == u"\u27A1":
                    if curr_page < len(PokeBot.help_pages) - 1:
                        curr_page += 1

                elif reaction.emoji == u"\u23E9":
                    curr_page = len(PokeBot.help_pages) - 1

                for button in buttons:
                    await msg.remove_reaction(button, ctx.author)

                if curr_page != previous_page:
                    await msg.edit(embed=PokeBot.help_pages[curr_page])
    else:
        await ctx.channel.send("No pokemon caught yet")

@PokeBot.command()
async def tester(ctx):
    channel = ctx.channel
    user = ctx.author.id

    # Generates pokemon and displays a gif for the user to guess the name
    pokemon = initialize_pokemon()
    pokemon_name = pokemon['Name']
    wild_pokemon_embed = create_wild_embed(pokemon)
    await ctx.channel.send(embed=wild_pokemon_embed)
    print(pokemon_name)

    # Validates the name is guessed correctly
    def check(m):
        return m.content.upper() == pokemon_name.upper() and m.channel == channel

    msg = await PokeBot.wait_for('message', check=check)
    caught_embed = create_caught_embed(pokemon_name)
    await channel.send(embed=caught_embed)

    # Initial Entry if json file is empty
    user = msg.author.id  # Person guessed gets the pokemon
    pokemon_list = [json.dumps(pokemon)]
    new_pokemon = {user: pokemon_list}

    # Try to open the json file to load its data, if empty: initialize
    try:
        with open("pokemon_storage.json", "r") as data_file:
            data = json.load(data_file)
    except json.decoder.JSONDecodeError:
        with open("pokemon_storage.json", "w") as data_file:
            json.dump(new_pokemon, data_file)
    else:
        # Either adds pokemon to user's existing list
        if str(user) in data:
            data[str(user)].append(json.dumps(pokemon))
            data.update(data)
            with open("pokemon_storage.json", "w") as data_file:
                json.dump(data, data_file)
        else:
            # Or creates a new list and adds their first pokemon
            data[str(user)] = []
            data[str(user)].append(json.dumps(pokemon))
            data.update(data)
            with open("pokemon_storage.json", "w") as data_file:
                json.dump(data, data_file)

@PokeBot.event
async def on_message(ctx):
    user = ctx.author.id
    channel = ctx.channel

    if user not in cooldown:
        cooldown[user] = 1
    print(cooldown)

    # Ensures the bot doesn't interact with itself
    if ctx.author == PokeBot.user:
        return
    # Random spawn triggered by any message
    if ctx.content.startswith(''):
        channel = ctx.channel
        user = ctx.author.id
        spawn = random.randint(0, 10)  # Small chance each message of spawning a Pokemon

        if str(channel) not in current_channels:  # Blocks users on cooldown and non-whitelisted channels
            spawn = 300
        if cooldown[user] != 1:
            spawn = 200
            cooldown[user] -= 1
        if user in bots:
            print("test")
            spawn = 100
        print(spawn)

        if spawn == 1:
            cooldown[user] += 10
            print(cooldown)

            # Generates pokemon and displays a gif for the user to guess the name
            pokemon = initialize_pokemon()
            pokemon_name = pokemon['Name']
            wild_pokemon_embed = create_wild_embed(pokemon)
            await ctx.channel.send(embed=wild_pokemon_embed)

            # Validates if name is correct
            def check(m):
                return m.content.upper() == pokemon_name.upper() and m.channel == channel

            msg = await PokeBot.wait_for('message', check=check)
            caught_embed = create_caught_embed(pokemon_name)
            await channel.send(embed=caught_embed)

            # Initial Entry if json file is empty
            user = msg.author.id  # Person guessed gets the pokemon
            pokemon_list = [json.dumps(pokemon)]
            new_pokemon = {user: pokemon_list}

            # Try to open the json file to load its data, if empty: initialize
            try:
                with open("pokemon_storage.json", "r") as data_file:
                    data = json.load(data_file)
            except json.decoder.JSONDecodeError:
                with open("pokemon_storage.json", "w") as data_file:
                    json.dump(new_pokemon, data_file)
            else:
                # Either adds pokemon to user's existing list
                if str(user) in data:
                    data[str(user)].append(json.dumps(pokemon))
                    data.update(data)
                    with open("pokemon_storage.json", "w") as data_file:
                        json.dump(data, data_file)
                else:
                    # Or creates a new list and adds their first pokemon
                    data[str(user)] = []
                    data[str(user)].append(json.dumps(pokemon))
                    data.update(data)
                    with open("pokemon_storage.json", "w") as data_file:
                        json.dump(data, data_file)
    await PokeBot.process_commands(ctx)

my_secret = os.environ['token']
keep_alive()
PokeBot.run(my_secret)
