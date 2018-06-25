"""
Copyright 2018 Andistar12 

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import discord
import os.path
import sys
import io
from PIL import Image

# Gets the bytes from an image
def get_pillowimage_bytes(image):
    img_bytes_arr = io.BytesIO()
    image.save(img_bytes_arr, format="JPEG")
    return img_bytes_arr.getvalue()

# Info
print("\nThis utility creates a 49-emoji discord message from one image.")
print("Given an input image, it splits it into 49, then uploads all 49 and the")
print("original image to a server it creates. It then sends you an invite to")
print("the server, where it will transfer ownership and then leave")
print("-----------------\n")

# Prompt user for image
imgFile = str(input("Enter file path to image: "))
if not os.path.isfile(imgFile):
    print("Error: File does not exist")
    sys.exit(1)
dot_split = imgFile.split(".")
if len(dot_split) > 2:
    print("Error: Name cannot have a . in it")
    sys.exit(1)
token = str(input("Enter bot token. Bot must be in at least one server with you: ")).rstrip()
if token is "":
    print("Error: blank token")
    sys.exit(1)
dimensions = 7 # This number can be changed to adjust how many 
imgName = imgFile.split(".")[0]

# Check that sending the spam won't go over char limit
if (len(imgName) + 4) * dimensions + 6 > 2000:
    print("Error: resulting message would be over 2000 chars")
    sys.exit(1)

# Initiate discord client
client = discord.Client()
on_ready_finished = False
@client.event
async def on_ready():
    global on_ready_finished
    print("Logged in as {0} (ID {1})".format(client.user.name, client.user.id))
    
    # Leave all servers the bot owns
    my_list = [server.id for server in client.servers]
    for sid in my_list:
        server = client.get_server(sid)
        if server.owner.id == client.user.id:
            print("Deleting server {0} (created on {1})".format(server.name, server.created_at))
            await client.delete_server(server)

    # Check that the owner is somewhere in our servers
    owner_present = False
    owner = (await client.application_info()).owner
    for server in client.servers:
        if owner.id in [m.id for m in server.members]:
            owner_present = True
    if not owner_present:
        print("Error: This bot must be in at least one shared server with its owner to send messages")
        await client.logout()
        return

    # Create pillow image, calculate width and height to crop by
    pillow_image = Image.open(imgFile)
    imgwidth, imgheight = pillow_image.size
    width = int(imgwidth / dimensions)
    height = int(imgheight / dimensions)
    count = 0

    # Create upload server and upload complete image
    print("Creating new upload server named " + imgName)
    new_server = await client.create_server(name=imgName, icon=get_pillowimage_bytes(pillow_image))
    orig_emoji = await client.create_custom_emoji(server=new_server, name=imgName+str(count), 
            image=get_pillowimage_bytes(pillow_image))
    bot_emoji = ""
    user_emoji = ""

    # Double for loop to adjust row and column
    for c in range(dimensions):
        for r in range(dimensions):
            # Crop image
            box = (r * width, c * height, r * width + width, c * height + height)
            cropped_image = pillow_image.crop(box)

            # Create and upload emoji
            emoji = await client.create_custom_emoji(server=new_server, name=imgName+str(count), 
                    image=get_pillowimage_bytes(cropped_image))
            print("Created new emoji {0} (ID {1})".format(emoji.name, emoji.id))
            
            # Add to message to send to user and server
            bot_emoji += "<:{0}:{1}>".format(emoji.name, emoji.id)
            user_emoji += ":" + emoji.name + ":"

            count += 1

        bot_emoji += "\n"
        user_emoji += "\n"

    # Build copypasta, send copypasta to server
    new_channel = await client.create_channel(new_server, "main")
    print("Created emoji spam message. Will be sent here and in the channel in server")
    print(user_emoji)
    await client.send_message(new_channel, "<:" + orig_emoji.name + ":" + orig_emoji.id + ">")
    await client.send_message(new_channel, "```" + user_emoji + "```")
    await client.send_message(new_channel, bot_emoji)

    # Notify bot owner with custom embed
    invite_link = await client.create_invite(new_channel)
    embed = discord.Embed(color=0xFF0000, 
            title="This invite goes to a server containing the emojis I created from the original image you gave me.",
            description="Upon joining this server, I will grant you server ownership and then leave it, giving you full control.")
    embed.set_author(name="Discord Server Created: " + imgName, url=invite_link)
    embed.set_thumbnail(url=new_server.icon_url)
    embed.add_field(name="Join now", value=invite_link, inline=True)
    print("Sending invite link to bot owner")
    await client.send_message(owner, embed=embed)
   
    on_ready_finished = True

@client.event
async def on_member_join(member):
    print("Detected member joined")
    # This should not be triggered before on_ready is done. We have a flag just in case
    global on_ready_finished
    if not on_ready_finished:
        print("Error: on_ready has not been completed yet")
        return
    
    # Transfer ownership to bot owner, then leave
    if member.server.owner.id == client.user.id:
        print("Transferring ownership to {0} and leaving server".format(member.name))
        await client.edit_server(member.server, owner=member)
        await client.leave_server(member.server)
        await client.logout()

# Begin
try:
    client.loop.run_until_complete(client.start(token))
except KeyboardInterrupt:
    client.loop.run_until_complete(client.logout())
except Exception as e:
    print("Error occurred: " + str(e))
    client.loop.run_until_complete(client.logout())
finally:
    client.loop.close()

print("Finished. Application quitting")
