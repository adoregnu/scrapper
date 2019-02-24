# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JavItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    title = scrapy.Field()
    plot = scrapy.Field()
    releasedate = scrapy.Field()
    runtime = scrapy.Field()
    actor = scrapy.Field()
    actor_thumb = scrapy.Field()
    director = scrapy.Field()
    set = scrapy.Field()
    studio = scrapy.Field()
    label = scrapy.Field()
    genre = scrapy.Field()
    thumb = scrapy.Field()
    rating = scrapy.Field()

class Article(scrapy.Item):
    id = scrapy.Field()
    cover_img_name = scrapy.Field()
    cover_img_url = scrapy.Field()
    file_name = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()