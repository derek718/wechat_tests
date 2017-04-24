# -*- coding: utf-8 -*-
from lib import *
import os
from lib.exceptions import *
import time

# os.system("/shells/pppoes.sh")
wechat = WechatSogouApi()
#实例化mysql类
mysql = mysql('mp_info')
guoke_mysql = guoke_mysql("public_number");

data = mysql.sqlquery('SELECT * FROM `mp_info` where is_py=0 ORDER BY RAND() LIMIT 10')

for item in data:
    # wechat.get_yesterday_time()
    # exit()

    gk_data = guoke_mysql.tables('public_number', 'gk').where({'wx_code': item['wx_hao']}).find(1)

    # 删除没有对应的公众号
    if (gk_data == None):
        mysql.tables("mp_info").where({'wx_hao': item['wx_hao']}).delete()
        continue

    link = wechat._get_public_list_link(item['wx_hao'])
    #判断link变量是否为空
    if not link:
        continue
    print (link)

    link = str(link)

    #获取此公众号最近文章
    wz_lists = wechat._get_wechat_wz_list(link)
    print (u'wz_:',len(wz_lists))
    if str(wz_lists) == 'ingcodes':
        break

    if (len(wz_lists) < 1):
        mysql.where_sql = " _id=%s" % (item['_id'])
        mysql.tables('mp_info').save({'is_py': 1})
        continue

    #关于此公众号可以插入的文章
    toinstData = list()
    gkIstData = list()

    for wz_item in wz_lists:
        if wz_item['type'] == '49':
            if not wz_item['content_url']:
                continue

            #真实URL
            soguourl = wz_item['content_url']
            zenshi_url = wechat.deal_get_real_url(url=wz_item['content_url'])
            if not zenshi_url:
                continue

            #阅读数
            comments = wechat.deal_get_wz_comment(url=soguourl)

            if not comments:
                continue

            instData = dict;
            instData ={'title': wz_item['title'],
             'source_url': wz_item['source_url'],
             'content_url': zenshi_url,
             'cover_url': wz_item['cover'],
             'description': wz_item['digest'],
             'date_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(wz_item['datetime'])),
             'mp_id': item['_id'],
             'author': wz_item['author'],
             'msg_index': wz_item['main'],
             'copyright_stat': wz_item['copyright_stat'],
             'qunfa_id': wz_item['qunfa_id'],
             'type': wz_item['type'],
             'like_count': comments['like_num'],
             'read_count': comments['read_num'],
             'comment_count': 0,
             'wx_hao':item['wx_hao']}

            up_data = {
                'category_id': int(gk_data['category_id']),
                'public_code': item['wx_hao'],
                'wx_url': zenshi_url,
                'title': wz_item['title'] if True else "",
                'position': wz_item['digest'] if True else "",
                'hit': int(comments['read_num']),
                'zan': comments['like_num'],
                # 'position':items['cover_url'],
                'thum': wz_item['cover'],
                'add_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(wz_item['datetime'])),
                'is_head': wz_item['main'],
                'intaddtime': int(time.time()),
            }
            toinstData.append(instData)
            gkIstData.append(up_data)

    for i in toinstData:
        mysql.tables('wechat_wz').add(i)

    mysql.where_sql = " _id=%s" % (item['_id'])
    mysql.tables('mp_info').save({'is_py':1})

    for ii in gkIstData:
        guoke_mysql.tables('article', 'gk').add(ii)
