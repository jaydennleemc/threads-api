import os
from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler
import json
import requests
import schedule
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        TimedRotatingFileHandler("app.log", when="midnight", interval=1, backupCount=7),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger()


def read_local_json():
    try:
        with open(f'{Path.cwd()}/python/last_thread.json', 'r', encoding='UTF-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def get_thread_caption(thread):
    if thread and 'thread_items' in thread and thread['thread_items']:
        caption = thread['thread_items'][0]["post"]["caption"]["text"]
        logger.info(f"Caption: {caption}")
        return caption
    else:
        logger.info("No caption found")
        return None


def get_thread_carousel_media(thread):
    if thread and 'thread_items' in thread and thread['thread_items']:
        has_carousel_media = thread['thread_items'][0]["post"].get("carousel_media")
        if has_carousel_media:
            logger.info("This Thread Has carousel media")
            carousel_media_urls = []
            for carousel_media in has_carousel_media:
                carousel_media_urls.append(carousel_media['image_versions2']['candidates'][0]['url'])
            logger.info(f"Carousel Media: {carousel_media_urls}")
            return carousel_media_urls
        else:
            logger.info("This Thread Doesn't have carousel media")
            return None
    else:
        logger.info("No thread items found")
        return None


def get_quoted_posts(thread):
    if thread and 'thread_items' in thread and thread['thread_items']:
        is_quoted_post = thread['thread_items'][0]["post"]["text_post_app_info"]['share_info'].get('quoted_post')
        if is_quoted_post:
            logger.info("This Thread is a Quoted Post")
            quoted_post = thread['thread_items'][0]["post"]["text_post_app_info"]['share_info']['quoted_post']
            logger.info(f"Quoted Post: {quoted_post}")
        else:
            logger.info("This Thread is not a Quoted Post")
            return None
    else:
        logger.info("No thread items found")
        return None


def get_thread_post_time(thread):
    if thread and 'thread_items' in thread and thread['thread_items']:
        taken_at = thread['thread_items'][0]["post"].get("taken_at")
        if taken_at:
            logger.info(f"Post Time: {taken_at}")
        else:
            logger.info("No post time found")
    else:
        logger.info("No thread items found")


def is_new_post(thread):
    local_post = read_local_json()
    if local_post is None:
        return True
    local_id = local_post['id']
    thread_id = thread['id']
    # Save the last thread to local json
    with open(f'{Path.cwd()}/python/last_thread.json', 'w+', encoding='UTF-8') as f:
        f.write(json.dumps(thread, indent=4, ensure_ascii=False))
    # Check if the thread is already saved
    if local_id == thread_id:
        logger.info("This Thread is already saved")
        return False
    else:
        logger.info("This Thread is not saved")
        return True


def check_last_thread_post(user_id):
    try:
        url = f'http://localhost:3000/api/users/{user_id}/threads'
        response = requests.get(url)
        if response.status_code != 200:
            push_discord_webhook(f"Thread API error, code = {response.status_code} & message = {response.text}")
            return

        response = response.json()
        threads = response["data"]["mediaData"]["threads"]
        last_thread_item = threads[1]

        if is_new_post(last_thread_item):
            logger.info("This is a new post")
            user = last_thread_item['thread_items'][0]["post"]["user"]
            logger.info(f"User: {user['username']}")
            caption = get_thread_caption(last_thread_item)
            push_message = f'New Post from {user["username"]}\ncaption:{caption}\n'
            has_carousel_media = get_thread_carousel_media(last_thread_item)
            if has_carousel_media:
                for media in has_carousel_media:
                    push_message += f'\n{media}'
            push_discord_webhook(push_message)
            # is_quoted_post = get_quoted_posts(last_thread_item)
            return
        else:
            logger.info("This is not a new post")
            return
    except Exception as e:
        logger.error(f'Exception error, message: {str(e)}')
        push_discord_webhook(f"Exception error, message: {str(e)}")


def push_discord_webhook(content):
    url = os.environ.get("WEBHOOK_URL")
    data = {
        "content": content
    }
    logger.info(f"Pushing Webhook To Discord: {data}")
    header = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json.dumps(data), headers=header)
    if response.status_code == 204:
        logger.info("Push Webhook To Discord successfully")
    else:
        logger.info("Push Webhook To Discord failed")


def job():
    user_ids = [
        "62206370355"
    ]
    for user_id in user_ids:
        check_last_thread_post(user_id)


if __name__ == '__main__':
    logger.info("Thread Monitor Started....")
    schedule.every(1).minutes.do(job)
    while True:
        schedule.run_pending()
