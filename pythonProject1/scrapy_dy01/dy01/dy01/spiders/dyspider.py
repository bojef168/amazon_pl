import scrapy


class DyspiderSpider(scrapy.Spider):
    name = "dyspider"
    allowed_domains = ["ssr1.scrape.center"]
    start_urls = ["https://ssr1.scrape.center"]

    def parse(self, response, **kwargs):
        for i in range(1, 11):
            new_url = f'https://ssr1.scrape.center/page/{i}'
           # print(new_url)
            yield scrapy.Request(new_url, callback=self.url_parse)

    def url_parse(self, response, **kwargs):
        div_list = response.xpath('//div[@class="el-card__body"]/div[@class="el-row"]')
        #抓取每一栏
        for dd in div_list:
            #抓取链接
            dy_href = dd.xpath('./div[2]/a/@href').extract_first()
            #抓取标题
            dy_tt = dd.xpath('./div[2]/a/h2/text()').extract_first()
            #拼接完整标题
            href = response.urljoin(dy_href)
            #print(href,dy_tt)
            yield scrapy.Request(href, meta={'dy_tt': dy_tt}, callback=self.parse_xiangqing)

    def parse_xiangqing(self, response, **kwargs):
        item = {}
        # 获取meta传递过来的电影标题
 #       dy_tt = response.meta['dy_tt']
        #print(dy_tt)
        # 获取市场地址、上映时间、剧情简介、导演
        dz = "".join(response.xpath('//div[@class="p-h el-col el-col-24 el-col-xs-16 el-col-sm-12"]/div[2]/span/text()').extract())
        time = response.xpath('//div[@class="p-h el-col el-col-24 el-col-xs-16 el-col-sm-12"]/div[3]/span/text()').extract_first(default='')
        jq = "".join(response.xpath('//div[@class="p-h el-col el-col-24 el-col-xs-16 el-col-sm-12"]/div[4]/h3/text() | //div[@class="p-h el-col el-col-24 el-col-xs-16 el-col-sm-12"]/div[4]/p/text()').extract()).replace("\n", "")
        dy = response.xpath('//p[@class="name text-center m-b-none m-t-xs"]/text()').extract_first(default='')
        #图片链接
        imgsrc = response.xpath('//*[@id="detail"]/div[1]/div/div/div[1]/div/div[1]/a/img/@src').extract_first()
#        print(dy_tt,dz,time,dy)

        item['dy_tt'] = response.meta['dy_tt']
        item['dz'] = dz
        item['time'] = time
        item['jq'] = jq
        item['dy'] = dy
        item['imgsrc'] = imgsrc
        yield (item)
