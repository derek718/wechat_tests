# -*- coding: utf-8 -*-
from .basic import WechatSogouBasic
from .exceptions import *
from lxml import etree
from lxml import html as hl
import string
from .db import mysql
from .guokedb import mysql as guokeMysql
import re
import time
import math

class WechatSogouApi(WechatSogouBasic):
    def __init__(self, **kwargs):
        super(WechatSogouApi, self).__init__(**kwargs)

    def _get_public_list_link(self, wechatid):
        html = self._get_wechat_text(wechatid)

        #获取指定公众号的文章列表页面
        url = list()
        info_urls = html.xpath(u"//div[@class='img-box']//a");
        for info_url in info_urls:
            url.append(info_url.attrib['href'])

        if len(url) < 1 or url == '':
            self._get_public_list_link(wechatid)
        return url[0] if url[0] else ''

    def _get_wechat_text(self, wechatid):
        url = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query=' + wechatid + '&ie=utf8&_sug_=n&_sug_type_='
        # url = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query=lizhilinzhongyan&ie=utf8&_sug_=n&_sug_type_='
	print(url)
        text = self._get(url)

        try:
            # page = hl.fromstring(text)
            page = etree.HTML(text)

            if u'相关的官方认证订阅号' in str(text):
                mysql.tables("mp_info").where({'wx_hao':wechatid}).delete();
                return ''
        except:
            self._get_wechat_text(wechatid)
        return page

    def _get_wechat_wz_list(self, url):
        try:
            text = self._get(url)
        except WechatSogouVcodeException:
            print(u'出现了验证')
            self._get_wechat_wz_list(url)

        try:
            # page = hl.fromstring(text)
            page = etree.HTML(text)
        except:
            self._get_wechat_wz_list(url)


        if str(text).find(u"为了保护你的网络安全，请输入验证码") != -1:
            print  u'为了保护你的网络安全，请输入验证码'
            return 'ingcodes'

        if u'为了您的安全请输入验证码' in str(text):
            print  u'为了保护你的网络安全，请输入验证码'
            return 'ingcodes'

        # 判断是否有msglist
        if u'msgList' not in str(text):
            print(u'mei you msgList')
            self._get_wechat_wz_list(url)

        #拿取文章列表
        gzh_wz_list_dict = self._deal_gzh_article_dict(self.get_gzh_wz_list_dict(text))
        return gzh_wz_list_dict

    def _get_wechat_wz_list_old(self, url):
        try:
            text = self._get(url)
        except WechatSogouVcodeException:
            print(u'出现了验证')
            self._get_wechat_wz_list(url)

        try:
            # page = hl.fromstring(text)
            page = etree.HTML(text)
        except:
            self._get_wechat_wz_list(url)

        # _str = unicode(str(text), "UTF-8")
        if str(text).find(u"为了保护你的网络安全，请输入验证码") != -1:
            print  u'为了保护你的网络安全，请输入验证码'
            self._get_wechat_wz_list(url)

        #公众号的所有文章
        last_wz_box = list()
        wz_fabu_time = list()
        wz_box = page.xpath(u"//div[@class='weui_media_box appmsg']")
        yestoday = self.get_yesterday_time()

        for i in wz_box:
            wz_fabu_time = i.xpath("div/p[2]/text()")[0]
            if str(wz_fabu_time) == yestoday:
                last_wz_box.append(i)

        # print (len(last_wz_box))
        # 这里是昨天的新闻
        wz_titles = list()
        wz_jjs = list()
        wz_urls = list()
        wz_logos = list()
        for z in last_wz_box:
            wz_title = z.xpath("div/h4/text()")[0]
            wz_titles.append(str(wz_title))

            # 最新文章的URL
            wz_url = z.xpath("div/h4/@hrefs")[0]
            wz_urls.append(str(wz_url))

            # 最新文章的简介
            wz_jj = z.xpath("div/p[1]/text()")[0]
            wz_jjs.append(str(wz_jj))

            # 要摘取文章的logo
            wz_logo = z.xpath("span/@style")[0]
            wz_logos.append(str(wz_logo))

        return self.inst_wz_data(wz_titles, wz_urls, wz_jjs, wz_logos)

    def inst_wz_data(self,*args):
        wz_titles = args[0]
        wz_urls = args[1]
        wz_jjs = args[2]
        wz_logos = args[3]

        ret_list = list()
        for i, v in enumerate(wz_urls):
            tmp = {
                "content_url": v,
                "title": wz_titles[i],
                "cover_url": wz_logos[i],
                "description": (wz_jjs[i]),
                "date_time": self.get_yesterday_time()
            }
            ret_list.append(tmp)
        return ret_list

    def get_gzh_wz_list_dict(self, text):
        try:
            msglist = re.findall("var msgList = (.+?)};", text, re.S)[0]
            msglist = msglist + '}'

            html = msglist
            html = html.replace('&#39;', '\'')
            html = html.replace('&amp;', '&')
            html = html.replace('&gt;', '>')
            html = html.replace('&lt;', '<')
            html = html.replace('&yen;', '¥')
            html = html.replace('amp;', '')
            html = html.replace('&lt;', '<')
            html = html.replace('&gt;', '>')
            html = html.replace('&nbsp;', ' ')
            html = html.replace('\\', '')

            msgdict = eval(html)
            return msgdict
        except:
            return False

    def _deal_gzh_article_dict(self, msgdict, **kwargs):
        """解析 公众号 群发消息

        Args:
            msgdict: 信息字典

        Returns:
            列表，均是字典，一定含有一下字段qunfa_id,datetime,type

            当type不同时，含有不同的字段，具体见文档
        """
        biz = kwargs.get('biz', '')
        uin = kwargs.get('uin', '')
        key = kwargs.get('key', '')
        items = list()

        if type(msgdict) != dict:
            return ''

        for listdic in msgdict['list']:
            item = dict()
            comm_msg_info = listdic['comm_msg_info']

            #只取前一天的文章
            if self.check_unix_time(comm_msg_info.get('datetime', '')) == False:
                continue
            item['qunfa_id'] = comm_msg_info.get('id', '')  # 不可判重，一次群发的消息的id是一样的
            item['datetime'] = comm_msg_info.get('datetime', '')
            item['type'] = str(comm_msg_info.get('type', ''))


            if item['type'] == '1':
                # 文字
                continue
            elif item['type'] == '3':
                # 图片
                continue
            elif item['type'] == '34':
                # 音频
                continue
            elif item['type'] == '49':
                # 图文
                app_msg_ext_info = listdic['app_msg_ext_info']
                url = app_msg_ext_info.get('content_url')
                if url:
                    url = 'http://mp.weixin.qq.com' + url if 'http://mp.weixin.qq.com' not in url else url
                else:
                    url = ''
                msg_index = 1
                item['main'] = msg_index
                item['title'] = app_msg_ext_info.get('title', '')
                item['digest'] = app_msg_ext_info.get('digest', '')
                item['fileid'] = app_msg_ext_info.get('fileid', '')
                item['content_url'] = url
                item['source_url'] = app_msg_ext_info.get('source_url', '')
                item['cover'] = app_msg_ext_info.get('cover', '')
                item['author'] = app_msg_ext_info.get('author', '')
                item['copyright_stat'] = app_msg_ext_info.get('copyright_stat', '')
                items.append(item)
                if app_msg_ext_info.get('is_multi', 0) == 1:
                    for multidic in app_msg_ext_info['multi_app_msg_item_list']:
                        url = multidic.get('content_url')
                        if url:
                            url = 'http://mp.weixin.qq.com' + url if 'http://mp.weixin.qq.com' not in url else url
                        else:
                            url = ''
                        itemnew = dict()
                        itemnew['qunfa_id'] = item['qunfa_id']
                        itemnew['datetime'] = item['datetime']
                        itemnew['type'] = item['type']
                        msg_index += 1
                        itemnew['main'] = msg_index
                        itemnew['title'] = multidic.get('title', '')
                        itemnew['digest'] = multidic.get('digest', '')
                        itemnew['fileid'] = multidic.get('fileid', '')
                        itemnew['content_url'] = url
                        itemnew['source_url'] = multidic.get('source_url', '')
                        itemnew['cover'] = multidic.get('cover', '')
                        itemnew['author'] = multidic.get('author', '')
                        itemnew['copyright_stat'] = multidic.get('copyright_stat', '')
                        items.append(itemnew)
                continue
            elif item['type'] == '62':
                continue
            items.append(item)
        return items

    def gzh_wz_calculate(self, **kwargs):

        gk_data = kwargs.get('gk_data',None)
        dicts = kwargs.get('dicts',None)

        print (type(dicts))
        print (dicts)
        exit()
        if dicts == False or len(dicts) <= 0:
            raise (u'微信id不能为空False')



        if gk_data == None or dicts== None :
            raise (u'微信id不能为空')

        instData={
            'release':0,#发布 （1/10）,
            'total_reading':0,#阅读总数
            'total_head':0,#头条阅读总数
            'max_head':0,#最高阅读数
            'total_zan':0,#总点赞数
            'average':0,#平均数
            'category_id':0,
            'public_code':'',
            'public_name':'',
            'logo':'',
            'addtime':int(time.time()),
            'gk_index' :0
        }

        #记录每一篇文章阅读数
        total_wz_hit = list()

        release_chishu = 0  # 发布次数
        release_total = len(dicts)  # 发布文章总数
        for i in dicts:
            #算出一天发布几次文章
            if int(i['is_head']) == 1:
                release_chishu+= 1
                instData['total_head'] += i['hit']
            else:
                release_chishu =1

            instData['total_reading'] += int(i['hit'])
            total_wz_hit.append(int(i['hit']))

            if release_total < 1 or instData['total_reading'] < 0:
                raise (u'没有数据')
            #总点赞数
            instData['total_zan'] += int(i['zan'])

        instData['public_code'] = gk_data['wx_code']
        instData['public_name'] = gk_data['name']
        instData['logo'] = gk_data['logo']
        instData['category_id'] = int(gk_data['category_id'])
        instData['release'] = str(release_chishu) + '/' + str(release_total)
        instData['average'] = int(int(instData['total_reading'])  / int(release_total))
        instData['max_head'] = max(total_wz_hit)
        instData['gk_index'] = self.gk_zhishu(instData)


        gk_mysql = guokeMysql('daydata', 'gk')
        gk_mysql.tables('daydata', 'gk').add(instData)


    def gk_zhishu(self,data,n=1):
        wrr = 0.75
        wrm = 0.05
        wra = 0.1
        wrh = 0.05
        wz = 0.05

        release = str(data['release']).split('/')

        R = (int(data['total_reading']) + 1) / (n * (int(release[1]) * 100000) + 1) *1000

        RM = ((int(data['max_head']) + 1) / 100001) *1000;

        #平均阅读
        RA = ((math.floor(data['total_reading'] / int(release[1])) + 1) / 100001) *1000;

        #头条阅读
        RH = ((100001 + 1) / (n * 100001)) *1000;

        #总点赞
        Z = ((int(data['total_zan']) + 1) / (n * (int(release[1]) * 10000) + 1)) *1000;

        NRI = wrr *R + wrm *RM + wra *RA + wrh *RH + wz *Z;
        return round(NRI,2);