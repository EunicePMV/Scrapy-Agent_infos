# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags

def remove_empty(value):
    if value == None:
        return value.replace(None, '').strip()
    return value.strip()

def filter_email(value):
    value = value.strip()
    if value == 'mailto:':
        return value.replace('mailto:', '')
    return value.replace('mailto:', '')

def filter_address(value):
    value = value.strip()
    if value == '':
        return None
    return value

def filter_name(value):
    value = value.replace('C/O', 'c/o').strip()
    value = value.replace('&amp;', '&').strip()
    return value

class EplanSpiderItem(scrapy.Item):
    name = scrapy.Field(input_processor = MapCompose(remove_tags, filter_name), output_processor = TakeFirst())
    fax = scrapy.Field(input_processor = MapCompose(remove_tags, remove_empty), output_processor = TakeFirst())
    email = scrapy.Field(input_processor = MapCompose(remove_tags, filter_email), output_processor = TakeFirst())
    address = scrapy.Field(input_processor = MapCompose(filter_address), output_processor = TakeFirst())
    phone = scrapy.Field(input_processor = MapCompose(remove_tags, remove_empty), output_processor = TakeFirst())
    file_number = scrapy.Field(output_processor = TakeFirst())