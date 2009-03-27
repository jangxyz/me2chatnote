#!/usr/bin/python
# -*- encoding: utf-8 -*-

import sys
if len(sys.argv) != 3:
    sys.exit('Usage: %s ACCESS_TOKEN ACCESS_TOKEN_SECRET' % sys.argv[0])
ACCESS_TOKEN = (sys.argv[1], sys.argv[2])

from me2day import Me2day
from springnote import Springnote

if __name__ == '__main__':

    # fetch from me2day
    users = ['jangxyz', 'loocaworld', 'agiletalk']
    posts = []
    [posts.extend( Me2day.posts(username, tag='woc') ) for username in users]

    # decorate
    posts.sort(lambda x, y: +1 if x.pubDate < y.pubDate else -1)
    items = ["%s: %s (%s)" % (post.author.nickname, post.body, post.pubDate) for post in posts]

    # save to springnote
    page = Springnote(ACCESS_TOKEN).page('springmemo', 2996232)
    page.source  = u"""<div>
        이 페이지는 me2chatnote에 의해서 자동으로 생성된 페이지입니다. <br />
        %s의 글들 중 'woc'라는 태그가 들어간 글을 수집했습니다.
    </div>""" % ', '.join(users)
    page.source += """<ul><li>%s</li></ul>""" % '</li><li>'.join(items)
    page.tags = ["woc", "me2chatnote"]
    page.save()
    print "successfully posted %s items" % len(posts)

