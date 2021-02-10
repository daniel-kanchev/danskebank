import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from danskebank.items import Article


class DanskeSpider(scrapy.Spider):
    name = 'danske'
    start_urls = ['https://danskebank.co.uk/about-us/news-and-insights']

    def parse(self, response):
        links = response.xpath('//li[@class="overview-item"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('(//div[@class="meta"]/span/text())[1]').get()
        if date:
            date = datetime.strptime(date.strip(), '%d. %b. %Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="row article-body"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
