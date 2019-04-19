from scrapy.spider import Spider,Request
from MicroBlog.items import MicroblogItem
from scrapy.conf import settings
from bs4 import BeautifulSoup
import os.path
import time,datetime
import json
import re
import csv

base_usrinfo_url = 'https://m.weibo.cn/api/container/getIndex?uid=%s&containerid=100505%s'
base_usr_mblogs_url = 'https://m.weibo.cn/api/container/getIndex?uid=%s&containerid=%s&page=%s'

base_mblog_url = 'https://m.weibo.cn/status/%s'
base_comments_url = "https://m.weibo.cn/api/comments/show?id=%s&page=%s"
base_reposts_url = 'https://m.weibo.cn/api/statuses/repostTimeline?id=%s&page=%s'

base_usrdetail_url = "https://m.weibo.cn/api/container/getIndex?containerid=230283%s_-_INFO"

class WeiboCrawl(Spider):
    name = 'weiboCrawl'

    def __init__(self,mblog_id=None,*args,**kwargs):
        super(WeiboCrawl, self).__init__(*args,**kwargs)
        self.mblog_url = base_mblog_url % (mblog_id)

    def start_requests(self):
        yield Request(self.mblog_url,callback=self.parse)

    def parse(self, response):
        pattern = r'var \$render_data = \[((.|\s)*?})\]'
        raw_data = re.search(pattern,response.text)
        raw_data = raw_data.group(1)
        json_data = json.loads(raw_data)
        status = json_data['status']
        try:
            is_retweeted = status['retweeted_status']
            mblog_id = is_retweeted['id']
            mblog_url = base_mblog_url % (mblog_id)
            return Request(mblog_url, callback=self.getBlog)
        except:
            pass
        pattern = r'var \$render_data = \[((.|\s)*?})\]'
        raw_data = re.search(pattern, response.text)
        raw_data = raw_data.group(1)
        json_data = json.loads(raw_data)

        status = json_data['status']
        items=self.putItem(status)
        usrdetail_url = base_usrdetail_url % (items['usr_id'])
        yield Request(url=usrdetail_url, meta={"item": items}, callback=self.getUsrDetail)

        if status['reposts_count']:
            reposts_url = base_reposts_url % (status['id'],str(1))
            yield Request(reposts_url,callback=self.getReposters)


    def putItem(self,status):
        user_info = status['user']
        items = MicroblogItem()
        items['mblog_id'] = str(status['id'])
        items['mblog_created_at'] = status['created_at']
        items['mblog_reposts_count'] = str(status['reposts_count'])
        items['mblog_comments_count'] = str(status['comments_count'])
        items['mblog_attitudes_count'] = str(status['attitudes_count'])
        try:
            items['mblog_raw_text'] = status['raw_text']
        except:
            items['mblog_raw_text'] = status['text']
        try:
            items['mblog_oid'] = str(status['retweeted_status']['id'])
        except:
            items['mblog_oid'] = str(status['id'])
        try:
            items['mblog_pid'] = str(status['pid'])
        except:
            items['mblog_pid'] = items['mblog_oid']


        items['usr_id'] = str(user_info['id'])
        items['usr_gender'] = user_info['gender']
        items['usr_name'] = user_info['screen_name']
        items['usr_blog_count'] = str(user_info['statuses_count'])
        items['usr_followers_count'] = str(user_info['followers_count'])
        items['usr_follow_count'] = str(user_info['follow_count'])
        items['usr_loc']="其他"

        return items

    def getReposters(self,response):
        json_data = json.loads(response.text)
        data = json_data['data']
        max = data['max']
        reposts_data = data['data']
        pattern = 'page=(\d+)'
        result = re.search(pattern,response.url)
        page_id = result.group(1)
        for item in reposts_data:
            items=self.putItem(item)
            usrdetail_url = base_usrdetail_url % (items['usr_id'])
            yield Request(url=usrdetail_url, meta={"item": items}, callback=self.getUsrDetail)
        if int(page_id) < int(max):
            reposts_url = re.sub(pattern,'page='+str(int(page_id)+1),response.url)
            yield Request(reposts_url,callback=self.getReposters)

    def getUsrDetail(self,response):
        items = response.meta["item"]
        json_data = json.loads(response.text)
        data = json_data['data']
        if len(data)>1:
            cards = data['cards']
            if len(cards) > 1:
                card_group = cards[1]['card_group']
                for card_info in card_group:
                    if 'item_name' in card_info.keys():
                        if card_info['item_name'] == '所在地':
                            location = card_info['item_content']
                            items['usr_loc'] = location
        yield items




















