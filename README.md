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
- Prevents user from accessing a dex without pokemon
- Prevents certain users to trigger spawns
- Prevents certain channels from allowing spawns
- Works with empty JSON file to start

Creating Embeds
- Creates a nice ui experience with embeds for things like : random spawns, dex navigation, caught notifications, and help screens

