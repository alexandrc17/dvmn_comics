import requests
import os
from dotenv import load_dotenv
import random


load_dotenv()
token = os.getenv("token")


def load_photo(url, file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, 'wb') as file:
        file.write(response.content)


def get_comics_img(id):
    url = "https://xkcd.com/{}/info.0.json".format(id)
    response = requests.get(url)
    response.raise_for_status()
    url_img = response.json()['img']
    filename = 'C:/Users/860159/Documents/GitHub/Comics_xkcd/comics_{}.png'.format(id)
    load_photo(url_img, filename)
    response = response.json()
    return response


def get_url_to_upload():
    url = "https://api.vk.com/method/photos.getWallUploadServer"
    payload = {"group_id": "188207986",
               "access_token": token,
               "v": "5.103"}
    response = requests.get(url, params=payload)
    url = response.json()["response"]['upload_url']
    return url


def save_photo(filename):
    with open(filename, 'rb') as file:
        url = get_url_to_upload()
        files = {
            'photo': file
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
    photo = response.json()
    return photo


def save_photo_in_album(filename):
    url = "https://api.vk.com/method/photos.saveWallPhoto"
    photo = save_photo(filename)
    payload = {"group_id": "188207986",
               "server": photo['server'],
               "photo": photo['photo'],
               "hash": photo['hash'],
               "access_token": token,
               "v": "5.103"}
    response = requests.post(url, params=payload)
    response = response.json()
    return response


def publish_photo(id_comics, file):
    title = get_comics_img(id_comics)['title']
    alt = get_comics_img(id_comics)['alt']
    photo = save_photo_in_album(file)['response'][0]
    url = "https://api.vk.com/method/wall.post"
    payload = {"owner_id": "-188207986",
               "from_group": "1",
               "message": title+"\n"+alt,
               "attachments": "photo"+str(photo['owner_id'])+"_"+str(photo['id']),
               "access_token": token,
               "v": "5.103"}
    response = requests.get(url, params=payload)
    print(response.json())


def main():
    max_comics = get_comics_img("")['num']
    id_comics = random.randint(1, max_comics)
    publish_photo(id_comics, "comics_"+str(id_comics)+".png")
    os.remove("comics_60.png")
    os.remove("comics_353.png")
    os.remove("comics_1641.png")
    os.remove("comics_1959.png")
    os.remove("comics_1058.png")
    os.remove("comics_" + str(id_comics) + ".png")


main()