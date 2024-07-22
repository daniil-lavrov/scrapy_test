from datetime import datetime

import scrapy

class QuotesSpider(scrapy.Spider):

    name = "goods_parser"

    start_urls = [
        'https://fix-price.com/catalog/kosmetika-i-gigiena/gigienicheskie-sredstva',
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def parse(self, response):
        for good in response.css('div.one-product-in-row'):

            link = good.css('a.title::attr(href)').get()

            if response.css('div.variants-count::text').get():
                variants = response.css('div.variants-count::text').get()
            else:
                variants = 0

            request = response.follow(link, callback=self.parse_good, meta={
                'RPC': good.css('::attr(id)').get(),
                'url': link,
                'title': good.css('a.title::text').get(),
                'timestamp': int(datetime.timestamp(datetime.now())),
                'variants': variants
            })
            yield request

    def parse_good(self, response):

        descr = response.css('div.description::text').getall()[2]
        list_of_key = response.css('div.properties p.property span.title::text').getall()
        list_of_values = response.css('div.properties p.property span.value::text').getall()
        if response.css('div.properties p.property span.title::text').get() == 'Бренд':
            brend = response.css('div.properties p.property span.value a::text').get()
            extra_info = dict(zip(list_of_key[1:], list_of_values))
        else:
            brend = None
            extra_info = dict(zip(list_of_key, list_of_values))

        metadata = {
            "__description": descr,
        }

        for key, value in extra_info.items():
            metadata[key] = value

        price_data = response.css(
            'div.product-details div.price-quantity-block div.price-wrapper meta[itemprop="price"]::attr(content)').get()

        main_image = response.css('div.product-images img::attr(src)').get()
        set_images = response.css('div.product-images img::attr(src)').getall()
        view69 = [img for img in set_images if '69x69' in img]

        section = response.css('div.crumb span.text::text').getall()[2]

        yield {
            "timestamp": response.meta['timestamp'],
            "RPC": response.meta['RPC'],
            "url": response.meta['url'],
            "title": response.meta['title'],
            "brend": brend,
            'section': section,
            "price_data": price_data,
            "assets": {
                "main_image": main_image,
                "set_images": set_images,
                "view69": view69
            },
            "metadata": metadata,
            'variants': response.meta['variants'],
        }



"""
        next_page = response.css('a.button.next::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
            "marketing_tags": ["str"],
                "brand": "str",
"""