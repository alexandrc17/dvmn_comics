import requests
import os
from dotenv import load_dotenv
import random


def load_photo(url, file_path):
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    if 'error' in response.json():
        raise requests.exceptions.HTTPError(response.json()['error'])
    with open(file_path, 'wb') as file:
        file.write(response.content)


def get_comics_info(id_comics=''):
    url = "https://xkcd.com/{}/info.0.json".format(id_comics)
    response = requests.get(url)
    response.raise_for_status()
    response = response.json()
    if 'error' in response:
        raise requests.exceptions.HTTPError(response['error'])
    return response


def get_comics_img(id_comics=''):
    url_img = get_comics_info(id_comics)['img']
    filename = '.\\comics_{}.png'.format(id_comics)
    load_photo(url_img, filename)


def get_url_to_upload():
    token_vk = os.getenv("TOKEN_VK")
    url = "https://api.vk.com/method/photos.getWallUploadServer"
    payload = {"group_id": "188207986",
               "access_token": token_vk,
               "v": "5.103"}
    response = requests.get(url, params=payload)
    if 'error' in response.json():
        raise requests.exceptions.HTTPError(response.json()['error'])
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
        if 'error' in response.json():
            raise requests.exceptions.HTTPError(response.json()['error'])
    photo = response.json()
    return photo


def save_photo_in_album(filename):
    token_vk = os.getenv("TOKEN_VK")
    url = "https://api.vk.com/method/photos.saveWallPhoto"
    photo = save_photo(filename)
    payload = {"group_id": "188207986",
               "server": photo['server'],
               "photo": photo['photo'],
               "hash": photo['hash'],
               "access_token": token_vk,
               "v": "5.103"}
    response = requests.post(url, params=payload)
    response = response.json()
    if 'error' in response:
        raise requests.exceptions.HTTPError(response['error'])
    return response


def publish_photo(id_comics, file):
    token_vk = os.getenv("TOKEN_VK")
    title = get_comics_info(id_comics)['title']
    alt = get_comics_info(id_comics)['alt']
    get_comics_img(id_comics)
    photo = save_photo_in_album(file)['response'][0]
    url = "https://api.vk.com/method/wall.post"
    payload = {"owner_id": "-188207986",
               "from_group": "1",
               "message": title+"\n"+alt,
               "attachments": "photo{}_{}".format(str(photo['owner_id']), str(photo['id'])),
               "access_token": token_vk,
               "v": "5.103"}
    response = requests.get(url, params=payload)
    if 'error' in response.json():
        raise requests.exceptions.HTTPError(response.json()['error'])


def main():
    load_dotenv()
    max_comics = get_comics_info()['num']
    id_comics = random.randint(1, max_comics)
    publish_photo(id_comics, ".\\comics_{}.png".format(str(id_comics)))
    os.remove("comics_{}.png".format(str(id_comics)))


if __name__ == '__main__':
    main()