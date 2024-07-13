from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import random

discord_webhook = "https://discord.com/api/webhooks/1247945031919079455/v8rtv3davztoFHpPePTfsEoz-7THvzmXB6vVNRxXq35rNdFibO-S31PxB2d6qEhYZxN2"

data1 = {
    "icon_1": "https://upload-static.hoyoverse.com/event/2021/02/25/22542ef6122f5ad4ac1c3834d11cdfb4_8505332314511574414.png",
    "name_1": "Fine Enhancement Ore",
    "cnt_1": 3,
    "icon_2": "https://upload-static.hoyoverse.com/event/2021/02/25/22542ef6122f5ad4ac1c3834d11cdfb4_8505332314511574414.png",
    "name_2": "Fine Enhancement Ore",
    "cnt_2": 3,
    "refresh": "1d 4h 0m ",
    "days": 27,
    "end_of_month": False,
}

data2 = {
    "icon_1": "https://upload-static.hoyoverse.com/event/2021/02/25/22542ef6122f5ad4ac1c3834d11cdfb4_8505332314511574414.png",
    "name_1": "Fine Enhancement Ore",
    "cnt_1": 3,
    "end_of_month": True,
    "refresh": "20 min",
    "days": 1,
}

def create_card(data: dict) -> Image.Image: 
    """
    The `create_card` function generates a card image with various elements such as icons, text, and
    portraits based on input data.
    
    Author - Liam Scott
    Last update - 07/12/2024
    @param data (dict) - The `data` parameter in the `create_card` function seems to be a dictionary
    containing various information needed to create a card. Here is a breakdown of the key-value pairs
    in the `data` dictionary:
    @returns The `create_card` function returns an image with various elements such as icons, text, and
    portraits pasted onto a base card template. The final image represents a card with information about
    rewards, days checked in, and potential future rewards.
    
    """
    base_number = random.randint(1, 9)
    base = Image.open(f'assets/cards/{base_number}.png')
    base = base.convert('RGB')

    frame = Image.open('assets/other_art/UI_Frm_AlchemySimCodexPage_Bg.png')
    base.paste(frame, (20, 68),frame)
    base.paste(frame, (20, 284),frame)

    icon_1 = Image.open(BytesIO(requests.get(data['icon_1']).content))
    icon_1 = icon_1.resize((100, 100))
    if icon_1.mode != 'RGBA':
        icon_1 = icon_1.convert('RGBA')
    
    if not data['end_of_month']:
        icon_2 = Image.open(BytesIO(requests.get(data['icon_2']).content))
        icon_2 = icon_2.resize((100, 100))
        if icon_2.mode != 'RGBA':
            icon_2 = icon_2.convert('RGBA')
        base.paste(icon_2, (40, 304), icon_2)
    
    base.paste(icon_1, (40, 88), icon_1)

    d = ImageDraw.Draw(base)
    font = ImageFont.load_default()
    font_reward = font.font_variant(size=34)
    font_day_title = font.font_variant(size=24)

    d.text((180, 80), "Today you got:", font=font_day_title, fill="Black")
    d.text((180, 120), f"{data['name_1']} x{data['cnt_1']}", font=font_reward, fill="pink")
    d.text((179, 119), f"{data['name_1']} x{data['cnt_1']}", font=font_reward, fill="purple")

    if data['end_of_month']:
        sticker_number = random.randint(2, 153)
        sticker = Image.open(f'assets/character_stickers/{sticker_number}.png')
        sticker = sticker.resize((100, 100))
        if sticker.mode != 'RGBA':
            sticker = sticker.convert('RGBA')
        base.paste(sticker, (40, 304), sticker)
        d.text((180, 300), "No More rewards this month!", font=font_day_title, fill="Black")
        d.text((180, 340), f"You have claimed all rewards this month!\nCome back in {data['refresh']}\nto see next months rewards!", font=font_day_title, fill="pink")
        d.text((179, 339), f"You have claimed all rewards this month!\nCome back in {data['refresh']}\nto see next months rewards!", font=font_day_title, fill="purple")
    else:
        d.text((180, 300), f"In {data['refresh']} you will get:", font=font_day_title, fill="Black")
        d.text((180, 340), f"{data['name_2']} x{data['cnt_2']}", font=font_reward, fill="pink")
        d.text((179, 339), f"{data['name_2']} x{data['cnt_2']}", font=font_reward, fill="purple")

    if data['days'] == 1:
        d.text((865, 20), f"Checked in", font=ImageFont.load_default().font_variant(size=24), fill="black")
        d.text((912, 62), f"{data['days']}", font=ImageFont.load_default().font_variant(size=35), fill="pink")
        d.text((910, 60), f"{data['days']}", font=ImageFont.load_default().font_variant(size=35), fill="black")
        d.text((835, 100), f"day this month!", font=ImageFont.load_default().font_variant(size=24), fill="black")
    else:
        d.text((865, 20), f"Checked in", font=ImageFont.load_default().font_variant(size=24), fill="black")
        d.text((902, 62), f"{data['days']}", font=ImageFont.load_default().font_variant(size=35), fill="pink")
        d.text((900, 60), f"{data['days']}", font=ImageFont.load_default().font_variant(size=35), fill="black")
        d.text((835, 100), f"days this month!", font=ImageFont.load_default().font_variant(size=23), fill="black")

    portrait_number = random.randint(2, 32)
    portrait = Image.open(f'assets/car_dec/{portrait_number}.png')
    if portrait.mode != 'RGBA':
        portrait = portrait.convert('RGBA')
    base.paste(portrait, (630, 422), portrait)
    

    return base


def send_card(data: dict):
    """
    The function `send_card` sends a card image to a Discord webhook along with a message indicating
    that a user has signed in.
    
    Author - Liam Scott
    Last update - 07/12/2024
    @param data (dict) - The `send_card` function takes a dictionary `data` as input, which is used to
    create a card with information. The function then sends this card as a message to a Discord webhook.
    
    """
    photo = create_card(data)
    name = "Test"

    data = {
  "content": "**__NAME__** Has signed in!",
}
    photo.save('assets/junk/Card.png')
    files = {'file': open('Card.png', 'rb')}
    requests.post(discord_webhook, data, files=files)

# The `if __name__ == "__main__":` block in Python is used to check whether the current script is
# being run directly by the Python interpreter or if it is being imported as a module into another
# script.
if __name__ == "__main__":
    send_card(data2)
    
