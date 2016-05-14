# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json

class MitCoursePipeline(object):
    def process_item(self, item, spider):
        filename = item['course_name']
        f = open("./course_corpus/"+filename+".json",'w')
        file_content = json.dumps(dict(item))
        f.write(file_content)
        f.close()
        return item
