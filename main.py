import requests
import os
from dotenv import load_dotenv
import random


def load_photo(url, file_path):
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, 'wb') as file:
        file.write(response.content)


def get_comics_info(id_comics=''):
    url = "https://xkcd.com/{}/info.0.json".format(id_comics)
    response = requests.get(url)
    response.raise_for_status()
    response = response.json()
    return response


def get_comics_img(id_comics=''):
    url_img = get_comics_info(id_comics)['img']
    filename = '.\\comics_{}.png'.format(id_comics)
    load_photo(url_img, filename)


def get_url_to_upload(token_vk):
    url = "https://api.vk.com/method/photos.getWallUploadServer"
    payload = {"group_id": "188207986",
               "access_token": token_vk,
               "v": "5.103"}
    response = requests.get(url, params=payload)
    if 'error' in response.json():
        raise requests.exceptions.HTTPError(response.json()['error'])
    url = response.json()["response"]['upload_url']

    return url


def upload_photo(filename, token_vk):
    with open(filename, 'rb') as file:
        url = get_url_to_upload(token_vk)
        files = {
            'photo': file
        }
        response = requests.post(url, files=files)
        if 'error' in response.json():
            raise requests.exceptions.HTTPError(response.json()['error'])
    photo_params = response.json()
    return photo_params


def save_photo_in_album(filename, token_vk):
    url = "https://api.vk.com/method/photos.saveWallPhoto"
    photo = upload_photo(filename, token_vk)
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


def publish_photo(id_comics, file, token_vk):
    description = get_comics_info(id_comics)
    title = description['title']
    alt = description['alt']
    get_comics_img(id_comics)
    photo = save_photo_in_album(file, token_vk)['response'][0]
    url = "https://api.vk.com/method/wall.post"
    payload = {"owner_id": "-188207986",
               "from_group": "1",
               "message": title + "\n" + alt,
               "attachments": "photo{}_{}".format(photo['owner_id'], photo['id']),
               "access_token": token_vk,
               "v": "5.103"}
    response = requests.get(url, params=payload)
    if 'error' in response.json():
        raise requests.exceptions.HTTPError(response.json()['error'])


def main():
    load_dotenv()
    token_vk = os.getenv("TOKEN_VK")
    max_comics = get_comics_info()['num']
    id_comics = random.randint(1, max_comics)
    try:
        publish_photo(id_comics, "comics_{}.png".format(id_comics), token_vk)
        os.remove("comics_{}.png".format(id_comics))
    except:
        os.remove("comics_{}.png".format(id_comics))
        raise ValueError("Ошибка")


if __name__ == '__main__':
    main()
