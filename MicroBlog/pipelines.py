# -*- coding: utf-8 -*-
import MySQLdb

dbuser = 'root'
dbpass = '123456'
dbname = 'MicroBlog'
dbhost = 'localhost'
dbport = '3306'

class MicroblogPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect(user=dbuser, passwd=dbpass, db=dbname, host=dbhost, charset="utf8",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            self.cursor.execute("""INSERT ignore INTO WeiboInfo(mblog_id,mblog_created_at,mblog_reposts_count,mblog_comments_count,mblog_attitudes_count,mblog_raw_text,mblog_pid,mblog_oid,usr_id)
                                        VALUES (%s, %s, %s, %s, %s,%s,%s,%s,%s)""",
                                (
                                    item['mblog_id'].encode('utf-8'),
                                    item['mblog_created_at'].encode('utf-8'),
                                    item['mblog_reposts_count'].encode('utf-8'),
                                    item['mblog_comments_count'].encode('utf-8'),
                                    item['mblog_attitudes_count'].encode('utf-8'),
                                    item['mblog_raw_text'].encode('utf-8'),
                                    item['mblog_pid'].encode('utf-8'),
                                    item['mblog_oid'].encode('utf-8'),
                                    item['usr_id'].encode('utf-8'),
                                )
                                )
            self.conn.commit()
        except MySQLdb.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
        try:
            self.cursor.execute("""INSERT ignore INTO UserInfo(usr_id,usr_gender,usr_name,usr_blog_count,usr_followers_count,usr_follow_count,usr_loc)
                                        VALUES (%s, %s, %s, %s, %s,%s,%s)""",
                                (
                                    item['usr_id'].encode('utf-8'),
                                    item['usr_gender'].encode('utf-8'),
                                    item['usr_name'].encode('utf-8'),
                                    item['usr_blog_count'].encode('utf-8'),
                                    item['usr_followers_count'].encode('utf-8'),
                                    item['usr_follow_count'].encode('utf-8'),
                                    item['usr_loc'].encode('utf-8'),
                                )
                                )
            self.conn.commit()
        except MySQLdb.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
        return item



