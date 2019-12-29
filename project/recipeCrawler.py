import scrapy

class RecipeSpider(scrapy.Spider):
    name = "recipe_spider"
    start_urls = ['https://www.yummly.com/recipes']

    def parse(self, response):
        SET_SELECTOR = ".recipe-card"
        NAME_SELECTOR = ".card-title::text"
        URL_SELECTOR = ".card-title::attr(href)"
        print("response.url = " + response.url)

        for recipe in response.css(SET_SELECTOR):
        	name = recipe.css(NAME_SELECTOR).extract_first()
        	link = "https://www.yummly.com" + recipe.css(URL_SELECTOR).extract_first()
        	print(link)
        	# request = response.follow(link, callback=self.parse)
         #    # Return it thanks to a generator
         #    yield request
            # yield {
            #     'url': recipe.css(URL_SELECTOR).extract_first(),
            #     'name': recipe.css(NAME_SELECTOR).extract_first()
            # }
            