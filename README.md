# Discord-Emoji-Maker

A utility to split an image into 7x7 and upload them as emojis to a Discord server, creating a sendable 49-emoji message. The result is creating a message full of emojis that represents a base image.

## Usage

1. Download or clone this repository
2. Launch the program in one of two ways
    * Run with pipenv shell (Run `pipenv install` then `pipenv run python3 ./discordemojimaker`). This assumes you have python3, pip, and pipenv on your system)
    * Run the provided Linux-only binary with `./discordemojimaker`
3. Input the image to make emojis of. This is a file path
4. Input the token of the bot you wish to use. You must be in at least one server with said bot, or else
5. Once the bot generates the emojis, accept the invite it gives you.
6. The resulting emojis will be posted in the server you join

## Requirements
* Running from source file: pip libraries `discord` and `pillow`
* Running from binary: a Linux environment
* A .jpg or .png file to be split up
* A bot with bot token on-hand. Learn about creating bots [here](https://discordapp.com/developers/docs/intro)

## Notes
* It is recommended that you use a square image with length divisible by 7. 245px x 245px is fine.
* Bots can only be server owners of up to 10 servers. This utility makes the given bot delete all servers that it is an owner of (it will not leave any servers it is in, only if it is the owner)
* When the bot sends you the invite, the entire server is already up. The first person to join the server will be given ownership
* I am not liable for any damage you do to your servers. Use at your own risk.
