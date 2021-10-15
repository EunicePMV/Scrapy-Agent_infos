import scrapy
from scrapy.http import Request, FormRequest
import logging
from eplan_spider.items import EplanSpiderItem
from scrapy.loader import ItemLoader

class EplanningSpider(scrapy.Spider):
    name = 'eplanning'
    allowed_domains = ['eplanning.ie']
    start_urls = ['https://www.eplanning.ie']

    def __init__(self, county):
        self.county = county

    def parse(self, response):
        if self.county:
            county = response.xpath("//td[@colspan='5']//a[contains(@href, '"+ self.county +"')]/@href").get()
            yield Request(county,
                          callback=self.parse_county)
        else:
            logging.info('Scraping all county.')
            counties_url = response.xpath("//td[@colspan='5']/a/@href")[:-1].getall()
            for county in counties_url:
                yield Request(county,
                              callback=self.parse_county)

    def parse_county(self, response):
        received_url = response.xpath("//a[contains(@href, 'RECEIVED')]/@href").get()
        absolute_received_url = response.urljoin(received_url)
        yield Request(absolute_received_url,
                      callback=self.parse_form)

    def parse_form(self, response):
        yield FormRequest.from_response(response,
                                        formdata={'RdoTimeLimit': '42'},
                                        dont_filter=True,
                                        formxpath='(//form)[2]',
                                        callback=self.parse_result)

    def parse_result(self, response):
        rows = response.xpath("//table//tr")[1:]
        for row in rows:
            file_number_url = row.xpath(".//a/@href").get()
            absolute_file_number_url = response.urljoin(file_number_url)
            yield Request(absolute_file_number_url,
                          callback=self.parse_agent)

        pagination = response.xpath("//*[@class='pagination']//li//a/@href")[:-1].getall()
        for page in pagination:
            absolute_page_url = response.urljoin(page)
            yield Request(absolute_page_url,
                          callback=self.parse_result)

    def parse_agent(self, response):
        agent = response.xpath("//*[@id='DivAgents']/table//tr/td/text()").get()
        if agent == 'No Agent Associated with this Application':
            logging.info('Agent not found.')
        else:
            agent = response.xpath("//*[@id='DivAgents']/table//tr")
            l = ItemLoader(item=EplanSpiderItem(), selector=agent)
            
            l.add_xpath('name', './/th[contains(text(), "Name")]/following-sibling::td')
            l.add_xpath('phone', './/th[contains(text(), "Phone")]/following-sibling::td')
            l.add_xpath('fax', './/th[contains(text(), "Fax")]/following-sibling::td')
            l.add_xpath('email', './/th[contains(text(), "e-mail")]/following-sibling::td/a/@href')

            places = agent.xpath(".//td/text()")[1:5].getall()
            string = ''
            for place in places:
                string += place
                string += ' '
            l.add_value('address', string)

            l.add_value('file_number', response.url[-7:-2])

            yield l.load_item()