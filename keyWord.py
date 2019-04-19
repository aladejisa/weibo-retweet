# -*- coding: utf-8 -*-
import codecs
import sys
from textrank4zh import TextRank4Keyword
import MySQLdb
import re

text=""
result={}

dbuser = 'root'
dbpass = '123456'
dbname = 'MicroBlog'
dbhost = 'localhost'
dbport = '3306'

db = MySQLdb.connect(user=dbuser, passwd=dbpass, db=dbname, host=dbhost, charset="utf8",
                                    use_unicode=True)
cursor = db.cursor()
cursor.execute("SELECT mblog_raw_text from weiboinfo where mblog_oid = \""+sys.argv[1]+"\"")
data = cursor.fetchall()
db.close()
for i in range(len(data)):
    text+=(data[i][0])
text = re.sub(r"</?(.+?)>", "", text) # 去除标签
text = re.sub(r"\s+", "", text)  # 去除空白字符


tr4w = TextRank4Keyword()
tr4w.analyze(text=text, lower=True, window=2,
             vertex_source='all_filters', edge_source='all_filters')
for item in tr4w.get_keywords(11, word_min_len=1):
    result[item.word]= item.weight

file = open(sys.argv[1]+".txt", "w")
for k,v in result.items():
    line =  k+ "," + str(v) + "\n"
    file.write(line)
file.close()