# Pokemon-Discord-Bot
## Utility
Spawning
- Every message has a 1/10 chance of spawning a pokemon
- After a successful spawn, the user who spawned the pokemon will be on a 10 message cooldown to prevent spamming
- Guessing the pokemons name will result in you catching the pokemon
        
Storage
- Currently all the pokemon are store in a JSON file
- The key is the discord's user ID and the value is a list of all of their pokemon

Error Handling
- Prevents user from accessing a dex without any pokemon
- Prevents certain users to trigger spawns
- Prevents certain channels from allowing spawns
- Works with empty JSON file to start
- Ensures the bot doesnt interact with itself

Creating Embeds
- Creates a nice ui experience with embeds for things like : random spawns, dex navigation, caught notifications, and help screens

Information Formatting
- Formats information through embeds
- Organizes pokemon data based on stats, info, and its sprite (via a gif)

Dex Navigation
- Stores all pokemon of the given user as a list of embeds
- Allows for the user to flip through their pokemons via reaction buttons
- Constantly Checks whether or not the user has switched pages by adding a reaction
- Depending on the reaction, it will move through the different embeds representing a users dex
- Once a reactions is added, it will switch pages and remove all current reactions
- If nothing happens for 60 seconds, it will delete the message and embed

##Plans for the future
Battles
- Create a 1v1 battle system
- Add things like a move pool and action system to the bot

Level Up Pokemon
- Add xp to the pokemon
- Have a way of training, gaining xp, and even evolving

Misc Ideas
- Shops
- Currency
- Larger Storage
- Try large scale hosting
