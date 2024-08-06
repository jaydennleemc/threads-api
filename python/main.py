import os
from pathlib import Path
import json
import requests
import schedule
from dotenv import load_dotenv

load_dotenv()


def read_local_json():
    try:
        with open(f'{Path.cwd()}/python/last_thread.json', 'r', encoding='UTF-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def get_thread_caption(thread):
    caption = thread['thread_items'][0]["post"]["caption"]["text"]
    print(f"Caption: {caption}")
    return caption


def get_thread_carousel_media(thread):
    has_carousel_media = thread['thread_items'][0]["post"]["carousel_media"]
    if has_carousel_media:
        print("This Thread Has carousel media")
        carousel_media_urls = []
        for carousel_media in has_carousel_media:
            carousel_media_urls.append(carousel_media['image_versions2']['candidates'][0]['url'])
        print(f"Carousel Media: {carousel_media_urls}")
        return carousel_media_urls
    else:
        print("This Thread Doesn't have carousel media")
        return None


def get_quoted_posts(thread):
    is_quoted_post = thread['thread_items'][0]["post"]["text_post_app_info"]['share_info']['quoted_post']
    if is_quoted_post:
        print("This Thread is a Quoted Post")
        quoted_post = thread['thread_items'][0]["post"]["text_post_app_info"]['share_info']['quoted_post']
        print(f"Quoted Post: {quoted_post}")

    else:
        print("This Thread is not a Quoted Post")
        return None


def get_thread_post_time(thread):
    taken_at = thread['thread_items'][0]["post"]["taken_at"]
    print(f"Post Time: {taken_at}")


def is_new_post(thread):
    local_post = read_local_json()
    if local_post is None:
        return True
    local_id = local_post['id']
    thread_id = thread['id']
    if local_id == thread_id:
        print("This Thread is already saved")
        return False
    else:
        print("This Thread is not saved")
        with open('last_thread.json', 'w+', encoding='UTF-8') as f:
            f.write(json.dumps(thread, indent=4, ensure_ascii=False))
        return True


def check_last_thread_post(user_id):
    try:
        url = f'http://localhost:3000/api/users/{user_id}/threads'
        data = requests.get(url).json()
        threads = data["data"]["mediaData"]["threads"]
        last_thread_item = threads[1]

        if is_new_post(last_thread_item):
            print("This is a new post")
            user = last_thread_item['thread_items'][0]["post"]["user"]
            print(f"User: {user['username']}")
            caption = get_thread_caption(last_thread_item)
            push_message = f'''
            @everyone
            **New Post Alert**
            User:   {user['username']}
            Caption:    {caption}
            
            '''
            has_carousel_media = get_thread_carousel_media(last_thread_item)
            if has_carousel_media:
                for media in has_carousel_media:
                    push_message += f'''
                    {media}
                    
                    '''
            push_discord_webhook(push_message)
            # is_quoted_post = get_quoted_posts(last_thread_item)
            return
        else:
            print("This is not a new post")
            return
    except Exception as e:
        print(f"Error: {e}")
        push_discord_webhook(json.dumps({
            "message": "Thread Monitor Error",
            "error": str(e)
        }))


def push_discord_webhook(content):
    url = os.environ.get("WEBHOOK_URL")
    data = {
        "content": content
    }
    header = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json.dumps(data), headers=header)
    if response.status_code == 204:
        print("Push Webhook To Discord successfully")
    else:
        print("Push Webhook To Discord failed")


def job():
    user_ids = [
        "62206370355"
    ]
    for user_id in user_ids:
        check_last_thread_post(user_id)


if __name__ == '__main__':
    print("Thread Monitor Started....")
    schedule.every(1).minutes.do(job)
    while True:
        schedule.run_pending()
