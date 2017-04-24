# -*- coding: utf-8 -*-

from .base import WechatSogouBase
from selenium import webdriver
# from selenium.webdriver import PhantomJS
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from lxml import etree
from lxml import html
from exceptions import *
import datetime
import time
import requests
import re

import random
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class WechatSogouBasic(WechatSogouBase):
    def __init__(self, **kwargs):
        # 代理请求头
        self._agent = [
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        ]

    def _get(self, url, types='', **kwargs):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = self._agent[random.randint(0, len(self._agent) - 1)]
        dcap["phantomjs.page.settings.resourceTimeout"] = "5000"
        dcap["phantomjs.page.settings.loadImages"] = False

        driver = webdriver.PhantomJS(desired_capabilities=dcap)
        # driver.implicitly_wait(5)
        driver.get(url)
        html = driver.page_source

        if u'用户您好，您的访问过于频繁，为确认本次访问为正常用户行为，需要您协助验证' in str(html):
            raise WechatSogouVcodeException('weixin.sogou.com verification code')
        if u'未知错误，请稍后再试' in str(html):
            raise WechatSogouVcodeException('weixin.sogou.com wei zhi cuo wu')
        return html

    def _gets(self, url, rtype='get', **kwargs):
	referer = kwargs.get('referer', None)
        host = kwargs.get('host', None)

        if host:
            del kwargs['host']
        if referer:
            del kwargs['referer']

        headers = {
            "Host": host if host else 'weixin.sogou.com',
            "Upgrade-Insecure-Requests": '1',
            "User-Agent": self._agent[random.randint(0, len(self._agent) - 1)],
            "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            "Referer": referer if referer else 'http://weixin.sogou.com/',
            "Accept-Encoding": 'gzip, deflate, sdch',
            "Accept-Language": 'zh-CN,zh;q=0.8'
        }

        if rtype == 'get':
            #self._session.cookies.set
            self._session = requests.session()
            r = self._session.get(url, headers=headers, **kwargs)
        else:
            return ''

        if u'链接已过期' in r.text:
            return '链接已过期'
	#print(requests.codes.ok)
        #return ''
        if r.status_code == requests.codes.ok:
	    print(r.text)
	    return ''
            r.encoding = self._get_encoding_from_reponse(r)
            if u'用户您好，您的访问过于频繁，为确认本次访问为正常用户行为，需要您协助验证' in r.text:
                self._vcode_url = url
                print(u'用户您好，您的访问过于频繁，为确认本次访问为正常用户行为，需要您协助验证')
                #raise WechatSogouVcodeException('weixin.sogou.com verification code')
        else:
            raise WechatSogouRequestsException('requests status_code error', r.status_code)
        return r.text	
    def get_yesterday_time(self):
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)
        yesterday = today - oneday
        yesterdayArr = str(yesterday).split('-')

        m = int(yesterdayArr[1])

        d = int(yesterdayArr[2])

        yesterday = yesterdayArr[0] + u"年" + str(m) + u"月" + str(d) + u"日"
        return str(yesterday)


    # 获取搜狗微信文章上的真实链接
    def deal_get_real_url(self, url):
        try:
            url = url + '&uin=MjExMTY2MjUzNg=='
            text = requests.get(url, allow_redirects=False)
            return text.headers['Location']
        except:
            return ""

    def check_unix_time(self, wz_time):
        # 只要当的时间减去1天的文章
        now_time = datetime.datetime.today()
        now_time = datetime.datetime(now_time.year, now_time.month, now_time.day, 0, 0, 0)
        tmp_time = now_time + datetime.timedelta(days=-1)
        unixArr = time.strptime(str(tmp_time), '%Y-%m-%d %H:%M:%S')
        unixTime = time.mktime(unixArr)
        unix_time = int(unixTime)  # 昨天的时间戳

        # 文章时间
        wz_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(wz_time))
        wz_unixArr = time.strptime(str(wz_time_str), '%Y-%m-%d %H:%M:%S')
        wz_unixTime = time.mktime(wz_unixArr)
        wz_unixTime = int(wz_unixTime)

        if wz_unixTime >= unix_time and wz_unixTime < (unix_time + 24 * 60 * 60):
            return True
        else:
            return False

    def deal_get_wz_comment(self, **kwargs):
        url = kwargs.get('url', None)
        text = self._get(url)

        if not text:
            raise ('deal_content need param url or texWechatSogouExceptiont')
        # page = etree.HTML(text)

        sg_data = re.findall(u'window.sg_data={(.*?)}', text, re.S)
        if not sg_data:
            return ""
        sg_data = '{' + sg_data[0].replace(u'\r\n', '').replace(' ', '').replace(u'\n','') + '}'
        sg_data = re.findall(u'{src:"(.*?)",ver:"(.*?)",timestamp:"(.*?)",signature:"(.*?)"}', sg_data)
        sg_data = list(sg_data[0])
        comment_req_url = 'http://mp.weixin.qq.com/mp/getcomment?src=' + sg_data[0] + '&ver=' + sg_data[
            1] + '&timestamp=' + sg_data[2] + '&signature=' + sg_data[
                              3] + '&uin=&key=&pass_ticket=&wxtoken=&devicetype=&clientversion=0&x5=0'
        # comment_text = self._get(comment_req_url)
        #requests.adapters.DEFAULT_RETRIES = 5
	try:
            _reqs = requests.session()
            _reqs.keep_alive = False
            comment_text = _reqs.get(comment_req_url)

            comment_dict = eval(comment_text.text)
	except:
	    return ''
        if not  comment_dict:
            self.deal_get_real_url(url=url)

        ret_dict = dict
        ret_dict = {'read_num':comment_dict['read_num'], 'like_num':comment_dict['like_num']}
        return ret_dict
    def _get_encoding_from_reponse(self, r):
	encoding = requests.utils.get_encodings_from_content(r.text)
        return encoding[0] if encoding else requests.utils.get_encoding_from_headers(r.headers)
