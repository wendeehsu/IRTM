import scrapy

def Cleaning(rawList):
	if rawList == "" or rawList == " ":
		return False
	return True

class RecipeSpider(scrapy.Spider):
    name = "recipe_spider"
    start_urls = ['https://www.yummly.com/recipes']

    def parse(self, response):
        SET_SELECTOR = ".recipe-card"
        URL_SELECTOR = ".card-title::attr(href)"

        for recipe in response.css(SET_SELECTOR):
        	link = "https://www.yummly.com" + recipe.css(URL_SELECTOR).extract_first()
        	request = response.follow(link, callback=self.parseRecipe)
        	yield request
    
    def parseRecipe(self, response):
    	recipeName = response.css(".recipe-title::text").extract_first()
    	ingredients = response.css(".ingredient::text").extract()
    	ingredients = list(filter(Cleaning,ingredients))
    	print("recipeName = ", recipeName)
    	print(ingredients)

            