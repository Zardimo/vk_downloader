import requests
import os
import urllib3
from dotenv import load_dotenv
import webbrowser
import random


def get_comics_upload_url(access_token, group_id):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {
        'group_id' : group_id,
        'access_token' : access_token,
        'v' : 5.102
    }
    response = requests.get(url, params)
    return response.json()



def dowload_image(image_name, image_url):
    path = os.path.join(os.getcwd(), 'vk_comics')
    os.makedirs('vk_comics', exist_ok=True)
    response = requests.get(image_url, verify=False)
    response.raise_for_status()
    with open(os.path.join(path, image_name), 'wb') as image:
        image.write(response.content)


def get_comics_comment_and_name():
    response = requests.get('https://xkcd.com/info.0.json')
    response.raise_for_status()
    last_comics_num = response.json()['num']
    random_comics_num = random.randint(1, last_comics_num)
    comics_response = requests.get(
                        f'https://xkcd.com/{random_comics_num}/info.0.json')
    comics_response.raise_for_status()
    comics = comics_response.json()
    comics_comment = comics['alt']
    comics_url = comics['img']
    full_name_comics = f'{comics["title"]}.{os.path.splitext(comics_url)[1]}'
    dowload_image(full_name_comics, comics_url)
    return comics_comment, full_name_comics


def get_download_image_server(upload_url, group_id, image_path):
    with open(image_path, 'rb') as image:
        response = requests.post(upload_url,
                                params={'group_id' : group_id},
                                files={'photo' : image})
    return response.json()


def save_photo_on_server(access_token, server_val, photo_val,
                            hash_val, group_id):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params = {
        'access_token' : access_token,
        'group_id' : group_id,
        'server' : server_val,
        'photo' : photo_val,
        'hash' : hash_val,
        'v' : 5.102
    }
    response = requests.post(url, params)
    return response.json()


def post_photo_vk_club(owner_id, photo_id, access_token, group_id, message):
    url = 'https://api.vk.com/method/wall.post'
    photo = f'photo{owner_id}_{photo_id}'
    params = {
        'owner_id' : group_id*-1,
        'from_group' : 1,
        'access_token' : access_token,
        'attachments' : photo,
        'v' : 5.102,
        'message' : message
    }
    response = requests.post(url, params)
    return response.json()


if __name__ == '__main__':
    urllib3.disable_warnings()
    load_dotenv()
    access_token = os.getenv('ACCESS_TOKEN')
    group_id = 187000263
    upload_url = get_comics_upload_url(access_token,
                                group_id)['response']['upload_url']
    comics_comment, comics_name = get_comics_comment_and_name()
    image_path = os.path.join(os.getcwd(), 'vk_comics', comics_name)
    upload_image_server = get_download_image_server(upload_url,
                                                    group_id, image_path)
    server_val, photo_val, hash_val = [
                                    upload_image_server['server'], 
                                    upload_image_server['photo'],
                                    upload_image_server['hash']
                                    ]
    photo_data = save_photo_on_server(access_token, server_val, photo_val,
                                        hash_val, group_id)['response'][0]
    save_photo_on_server(access_token, server_val, photo_val,
                            hash_val, group_id)
    post_photo_vk_club(photo_data['owner_id'], photo_data['id'],
                        access_token, group_id, comics_comment)
    os.remove(image_path)