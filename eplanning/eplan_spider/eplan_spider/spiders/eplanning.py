import scrapy
from scrapy.http import Request, FormRequest


class EplanningSpider(scrapy.Spider):
    name = 'eplanning'
    allowed_domains = ['eplanning.ie']
    start_urls = ['https://www.eplanning.ie']

    def parse(self, response):
        # link for every county
        counties_url = response.xpath(".//td[@colspan='5']/a/@href")[:-1].getall()
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
        agent = response.xpath("//*[@id='DivAgents']/table//tr")
        if agent == []:
            pass
        else:
            name = agent.xpath(".//td/text()")[0].get().strip()
            address = agent.xpath(".//td/text()")[1:5].getall()
            phone = agent.xpath(".//th[contains(text(), 'Phone')]/following-sibling::td/text()").get()
            fax = agent.xpath(".//th[contains(text(), 'Fax')]/following-sibling::td/text()").get()
            email = agent.xpath(".//th[contains(text(), 'e-mail')]/following-sibling::td/text()").get()

            yield {'name': name,
                   'address': address,
                   'phone': phone,
                   'fax': fax,            
                   'email': email}
