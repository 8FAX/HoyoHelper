import requests
from PIL import Image
from io import BytesIO


def get_photo(url):
    headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "If-Modified-Since": "Fri, 05 Jul 2024 03:14:57 GMT",
    "If-None-Match": 'W/"66876531-22e"',
    "Priority": "u=0, i",
    "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "Sec-Ch-Ua-Mobile": "?1",
    "Sec-Ch-Ua-Platform": '"Android"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
}
    response = requests.get(url, headers=headers)
    image = Image.open(BytesIO(response.content))
    image.show()
    return image

if __name__ == "__main__":
    img = get_photo("https://8fax.github.io/HoyoHelper/assets/gi/cards/1.png")
    save = input("Do you want to save the image? (y/n): ")
    if save == "y":
        img.save("image.png")
    else:
        print("Image not saved.")
        