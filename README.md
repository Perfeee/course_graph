# course_graph
本项目是一个根据课程简介，画出课程图谱（仅包含先修课程和相关课程）的demo。运用到scrapy、BeautifulSoup、nltk、gensim、networlx等相关的python模块。

1、mit_course文件夹是跟scrapy网络爬虫相关的程序。


2、根目录的文件包含课程网页数据清洗和模型训练，以及一些程序执行过程当中保存的词典、模型数据等。

3、主要的两个程序文件是course_similarity.py(数据清洗、lda模型训练)和course_graph.py文件（构建图）
