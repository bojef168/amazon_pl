# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

class Dy01Pipeline:
    # 在爬虫开启的时候仅执行一次
    def open_spider(self, item):
        print('open------')
        self.f = open('dy.txt', 'w', encoding='UTF-8')

    # :实现对item数据的处理
    def process_item(self, item, spider):
        print('item----------')
        self.f.write(item['dy_tt'] + '\n')
        self.f.write(item['dz'] + '\n')
        self.f.write(item['time'] + '\n')
        self.f.write(item['jq'] + '\n')
        self.f.write(item['dy'] + '\n')
        self.f.write(item['imgsrc'] + '\n')
        return item

    # 在爬虫关闭的时候仅执行一次
    def close_spider(self, item):
        print('close-----')
        self.f.close()
