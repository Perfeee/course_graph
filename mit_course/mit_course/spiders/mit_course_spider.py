#!/usr/bin/env python
# coding=utf-8

import scrapy
from mit_course.items import MitCourseItem
from bs4 import BeautifulSoup,NavigableString
import random

class CourseSpider(scrapy.Spider):
    name = "course"
    allowed_domains = ["ocw.mit.edu"]
    start_urls = ["http://ocw.mit.edu/courses/"]
    def parse(self,response):
        soup = BeautifulSoup(response.body)
        tag_a = soup.find_all("a",rel="coursePreview",class_="preview")
        for i in range(200):        #总共似乎有几千门课
            url = random.choice(tag_a)["href"]
            #这种机械生成网址是有疏漏(Syllabus,404)的，最好还是加个解析函数抽取网址
            course_url = response.urljoin(url)+"/syllabus/" 
            yield scrapy.Request(course_url,callback=self.course_content_parse)
    

    def course_main_page(self,response):
        '''可从课程主页解析course_content_page网址，以及course_id'''
        pass
    
    def course_content_parse(self,response):
        
        soup = BeautifulSoup(response.body)
        item = MitCourseItem()
        
        name_tag = soup.find_all("div",id="breadcrumb")
        try:
            tag_a = name_tag[0].find_all('a')
            course_name = tag_a[-1].get_text()
            course_id_list = tag_a[-1]["href"].split("/")[-1].split("-")[:2]
            course_id = course_id_list[0]+course_id_list[1]
            item["course_name"] = course_name
            item["course_id"] = course_id
        except Exception as e:
            print(e)

        course_tag = soup.find_all("div",id="course_inner_section")
        tag_h2 = course_tag[0].find_all("h2",class_="subhead")
        course_desc = []
        course_pre = []
        course = set(["Description","Goals","Objective","Overview","Summary","Objectives"])
        for tag_b in tag_h2:
            #会错过其他课程内容的表述。
            if not course.isdisjoint(set(tag_b.get_text().split())):
                for tag_bb in tag_b.next_siblings:
                    if isinstance(tag_bb,NavigableString):
                        continue
                    if tag_bb.name != "h2":
                        course_desc.append(tag_bb.get_text())
                    else:
                        break
            elif "Prerequisites" in tag_b.get_text():
                for tag_bb in tag_b.next_siblings:
                    if isinstance(tag_bb,NavigableString):
                        continue
                    if tag_bb.name != "h2":
                        course_pre.append(tag_bb.get_text())
                    else: 
                        break
        item["course_prerequisites"] = course_pre
        item["course_description"] = course_desc 
        yield item


