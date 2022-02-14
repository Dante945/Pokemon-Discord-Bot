import os
import discord
import requests
import json
import random
from keep_alive import keep_alive


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
        sprite_link = f"https://play.pokemonshowdown.com/sprites/xyani-shiny/{pokemon_name}.gif"
    else:
        sprite_link = f"https://play.pokemonshowdown.com/sprites/xyani/{pokemon_name}.gif"

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


client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    # Ensures the bot doesnt interact with itself
    if message.author == client.user:
        return
    # Manually spawns a pokemon
    if message.content.startswith('%spawn'):
        channel = message.channel
        user = message.author.id
        spawn = 1
        if spawn == 1:
            # Generates pokemon and displays a gif for the user to guess the name
            pokemon = initialize_pokemon()
            await message.channel.send("Who's that Pokemon!")
            await message.channel.send(f"https://play.pokemonshowdown.com/sprites/xyani/{pokemon['Name']}.gif")

            # Validates if name is correct
            def check(m):
                return m.content.upper() == pokemon['Name'].upper() and m.channel == channel

            msg = await client.wait_for('message', check=check)
            await channel.send('correct!'.format(msg))

            # Initial Entry if json file is empty
            pokemon_list = [json.dumps(pokemon)]
            new_pokemon = {
                user: pokemon_list
            }

            # Try to open the json file to load its data, if empty: initialize
            try:
                with open("pokemon_storage.json", "r") as data_file:
                    data = json.load(data_file)
            except json.decoder.JSONDecodeError:
                with open("pokemon_storage.json", "w") as data_file:
                    json.dump(new_pokemon, data_file)
            else:
                # Either adds pokemon to users existing list
                if str(user) in data:
                    data[str(user)].append(json.dumps(pokemon))
                    data.update(data)
                    with open("pokemon_storage.json", "w") as data_file:
                        json.dump(data, data_file)
                else:
                    # Or creates new list and adds first pokemon
                    data[str(user)] = []
                    data[str(user)].append(json.dumps(pokemon))
                    data.update(data)
                    with open("pokemon_storage.json", "w") as data_file:
                        json.dump(data, data_file)

    # Displays a list of all pokemon caught by current user
    if message.content.startswith('%dex'):
        user = message.author.id
        with open("pokemon_storage.json", "r") as data_file:
            data = json.load(data_file)
        # Validates that the user has caught any pokemon yet
        if str(user) in data:
            user_data = data[str(user)]
            await message.channel.send("Here is your current Dex!:")
            await message.channel.send("Use '%info [dex number]' for more information")
            i = 1
            for entry in user_data:
                pokemon = json.loads(entry)
                await message.channel.send(f'#{i}: Level {pokemon["Level"]} {pokemon["Name"]}')
                i += 1
        else:
            await message.channel.send("No pokemon caught yet")

    if message.content.startswith('%info'):
        user = message.author.id
        with open("pokemon_storage.json", "r") as data_file:
            data = json.load(data_file)[str(user)]

        dex_number = int(message.content.split()[-1])
        # Validates the dex number
        if dex_number > 0 and dex_number <= len(data):

            # Loads and displays information about selected pokemon
            pokemon_json = data[dex_number - 1]
            pokemon = json.loads(pokemon_json)
            await message.channel.send(f"{pokemon['Sprite']}")
            await message.channel.send("**Info:**")
            await message.channel.send(f"Pokemon: {pokemon['Name'].title()}")
            await message.channel.send(f"Level: {pokemon['Level']}")
            if len(pokemon['Type']) > 1:
                await message.channel.send(f"Type: {pokemon['Type'][0].title()}/{pokemon['Type'][1].title()}")
            else:
                await message.channel.send(f"Type: {pokemon['Type'][0].title()}")
            await message.channel.send(f"Ability: {pokemon['Ability'].title()}")
            await message.channel.send("**Stats:**")
            await message.channel.send(
                f"Hp: {pokemon['Stats']['Hp']}\nAttack: {pokemon['Stats']['AtK']}\nSpecial Attack: {pokemon['Stats']['SpA']}\nDefense: {pokemon['Stats']['Def']}\nSpecial Defense: {pokemon['Stats']['SpD']}\nSpeed: {pokemon['Stats']['Spe']}")

        else:
            await message.channel.send(f"Invalid Dex Number!")

        # Random Spawn
    if message.content.startswith(''):
        channel = message.channel
        user = message.author.id
        spawn = random.randint(1, 30)
        if spawn == 1:
                # Generates pokemon and displays a gif for the user to guess the name
                pokemon = initialize_pokemon()
                await message.channel.send("Who's that Pokemon!")
                await message.channel.send(f"https://play.pokemonshowdown.com/sprites/xyani/{pokemon['Name']}.gif")

                # Validates if name is correct
                def check(m):
                    return m.content.upper() == pokemon['Name'].upper() and m.channel == channel

                msg = await client.wait_for('message', check=check)
                await channel.send('correct!'.format(msg))

                # Initial Entry if json file is empty
                pokemon_list = [json.dumps(pokemon)]
                new_pokemon = {
                    user: pokemon_list
                }

                # Try to open the json file to load its data, if empty: initialize
                try:
                    with open("pokemon_storage.json", "r") as data_file:
                        data = json.load(data_file)
                except json.decoder.JSONDecodeError:
                    with open("pokemon_storage.json", "w") as data_file:
                        json.dump(new_pokemon, data_file)
                else:
                    # Either adds pokemon to users existing list
                    if str(user) in data:
                        data[str(user)].append(json.dumps(pokemon))
                        data.update(data)
                        with open("pokemon_storage.json", "w") as data_file:
                            json.dump(data, data_file)
                    else:
                        # Or creates new list and adds first pokemon
                        data[str(user)] = []
                        data[str(user)].append(json.dumps(pokemon))
                        data.update(data)
                        with open("pokemon_storage.json", "w") as data_file:
                            json.dump(data, data_file)

my_secret = os.environ['token']
keep_alive()
client.run(my_secret)




