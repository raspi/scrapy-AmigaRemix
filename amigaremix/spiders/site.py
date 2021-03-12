from datetime import datetime

import scrapy

from amigaremix.items import Tune


class SiteSpider(scrapy.Spider):
    allowed_domains = [
        'amigaremix.com',
        'www.amigaremix.com',
    ]

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError()


class AllSpider(SiteSpider):
    name = 'all'
    start_urls = ['https://amigaremix.com/remixes/1']

    def parse(self, response: scrapy.http.Response):

        # Next page link
        next_page = response.xpath(
            "//div[@id='pager_one']/div[@class='subcontainer']/div[contains(@class, 'pageside') and contains(@class, 'pright')]/a/@href"
        ).get()

        if next_page is not None:
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse,
            )

        for row in response.xpath("//table[@id='remixtable']/tr[@class]"):
            # Get tunes
            addeddate = datetime.strptime(row.xpath("td[1]/text()").get(), "%Y-%m-%d")
            link = response.urljoin(row.xpath("td[2]/a/@href").get())
            title = row.xpath("td[2]/a/text()").get()
            arranger = row.xpath("td[3]/a/text()").get()
            composer = row.xpath("td[4]/text()").get()

            yield scrapy.Request(
                link,
                callback=self.dl_tune,
                meta={
                    "tune": Tune(
                        title=title,
                        arranger=arranger,
                        added=addeddate,
                        composer=composer,
                        data=None,
                    ),
                }
            )

    def dl_tune(self, response: scrapy.http.Response):
        ctype = response.headers.get('Content-Type').decode('utf-8')
        if ctype != 'audio/mpeg':
            raise ValueError(f"Invalid content-type '{ctype}'")

        tune: Tune = response.meta["tune"]
        tune.data = response.body
        yield tune
