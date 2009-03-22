#!/usr/bin/python

from me2day import Me2day
from springnote import Springnote

def get_post_from_me2day(users, tags):
    posts = []
    for username in users:
        posts += Me2day.posts(username, tags)
    return posts

def get_page_from_springnote(note, id):
    springnote_client = Springnote(access_token=(TOKEN_KEY, TOKEN_SECRET))
    return springnote_client.page(note, id)

def get_time_of_last_bullet(page):
    page.source
    return 1

def update_bullets(page, posts):
    page.source += '<br/>'.join([post.body for post in posts])
    page.save()

def decorate_posts(posts):
    posts

if __name__ == '__main__':

    page = Springnote(access_token=token).page('springmemo', 123)
    last_time = get_time_of_last_bullet(page)
    now = datetime.now()

    users = ['jangxyz', 'loocaworld', 'agiletalk']
    #posts = get_posts_from_me2day(users, 'woc')
    recent_woc_posts = lambda u: Me2day.posts(u, tag='woc', since=last_time, to=now)
    posts = []
    for username in users:
        posts += recent_woc_posts(username)

    posts = decorate_posts(posts)

    # merge
    update_bullets(page, posts)

