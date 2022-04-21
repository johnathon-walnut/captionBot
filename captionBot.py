import discord
import urllib.request
import random
import enum
import os
from wand.image import Image
from wand.font import Font
from wand.drawing import GRAVITY_TYPES, Drawing
from wand.image import COMPRESSION_TYPES

user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers={'User-Agent':user_agent,} 

client = discord.Client()

class Cap(enum.Enum):
    Text = 1

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

async def parse_message(message):
    msg = message.content
    args = msg.split()
    args[0] = args[0][1:]
    command = args[0]
    args.pop(0)
    return command, args

async def help_command(pMessage, args):
    if len(args) == 0:
        await pMessage.channel.send("""
        ```markdown
        #Commands:
            - help
            - caption 
        #My command prefix is ^```""")
    else:
        if args[0] == "help":
            await pMessage.channel.send("""
            ```markdown
            #Help command:
                - Shows a list of commands avilable```
            """)
        if args[0] == "caption":
            await pMessage.channel.send("""
            ```markdown
            #Caption command:
                - Applies a caption to the top of an image```
            """)

async def parse_attachments(attachments):
    return attachments[0].url
    ...

async def download_file(url):
    randomID = random.randint(1000000000000000000000, 99999999999999999999999999)
    file_name = "./images/" + str(randomID) + "_" + url[url.rindex("/") + 1:]
    print(f"File name: {file_name}")
    request = urllib.request.Request(url, None, headers)
    response = urllib.request.urlopen(request)
    data = response.read()
    with open(file_name, "wb") as f:
        f.write(data)
    return file_name

def replaceABwithC(input, pattern, replaceWith):
    return input.replace(pattern, replaceWith)

async def caption_image(pMessage, file_name, effect: Cap, caption):
    await pMessage.channel.send("Processing image... :nerd: ")
    try:
        with Image(filename=file_name) as image:
            if (effect == Cap.Text):
                with image.clone() as edited_image:
                    edited_image.coalesce()
                

                    image_width, image_height = edited_image.width, edited_image.height

                    font_size = image_width / 10

                    cap = caption.split()
                    top_word = ""
                    bottom_word = ""
                    word = ""
                    multi_line = False

                    if "|" in cap:
                        multi_line = True
                        temp = cap.index("|")
                        top = cap[:temp]
                        bottom = cap[temp + 1:]
                    
                        for w in top:
                            top_word += w + " "

                        for w in bottom:
                            bottom_word += w + " "
                    else:
                        for w in cap:
                            word += w + " "

                    impact_font = Font("C:/Windows/Fonts/impact.ttf", size=font_size, color="white", stroke_color="black", stroke_width=1)

                    for i in range(0, len(edited_image.sequence)):
                        with edited_image.sequence[i] as frame:
                            if multi_line == True:
                                frame.gravity = GRAVITY_TYPES[2] # North
                                frame.caption(top_word, font=impact_font)

                                frame.gravity = GRAVITY_TYPES[8] # South

                                frame.caption(bottom_word, font=impact_font)
                            else:
                                frame.gravity = GRAVITY_TYPES[2] # North

                                frame.caption(word, font=impact_font)

                    edited_image.optimize_layers()

                    extension = file_name[file_name.rindex(".") + 1:]
                    pattern = "/images/"
                    replace_with = "/captioned/"
                    caption_file_name = file_name[:file_name.rindex(".")] + ".caption." + extension
                    caption_file_name = replaceABwithC(caption_file_name, pattern, replace_with)
                    flip_image_bin = edited_image.make_blob()
                    with open(caption_file_name, "wb") as f:
                        f.write(flip_image_bin)

                if os.path.getsize(caption_file_name) > 7999999:
                    await pMessage.channel.send("Image too large to send, ask m-fed for it")
                else:
                    await pMessage.channel.send(file=discord.File(caption_file_name))
    except Exception as e:
        await pMessage.channel.send(e)
                
   


async def caption_command(pMessage, args):
    if len(args) == 0:
        await pMessage.channel.send("Captioning failed - no caption given.")
        return
    formatted_word = ""
    for word in args:
        formatted_word += word + " "
    print(f"Caption should be: {formatted_word}")
    url = await parse_attachments(pMessage.attachments)
    print(f"{url}")
    file_name = await download_file(url)
    await caption_image(pMessage, file_name, Cap.Text, formatted_word)
    ...

async def handle_command(message):
    command, args = await parse_message(message)
    args_amount = len(args)
    print(f"Command: {command} \nArguments ({args_amount}): {args} ")
    if command == "help":
        await help_command(message, args)
    if command == "caption":
        await caption_command(message, args)
    print("")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith("^"):
        await handle_command(message)

def run_bot():
    token = ""
    client.run(token)

run_bot()