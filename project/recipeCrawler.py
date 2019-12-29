import scrapy
import os
import json

def Cleaning(rawList):
	if rawList == "" or rawList == " ":
		return False
	return True

class RecipeSpider(scrapy.Spider):
	name = "recipe_spider"
	requiresRecipeNum = 10
	yummlyUrl = "https://mapi.yummly.com/mapi/v17/content/search?solr.seo_boost=new&start=1&maxResult=" + str(requiresRecipeNum) + "&fetchUserCollections=false&allowedContent=single_recipe&allowedContent=suggested_search&allowedContent=related_search&allowedContent=article&allowedContent=video&allowedContent=generic_cta&guided-search=true&solr.view_type=search_internal"
	start_urls = [yummlyUrl]
	path = "recipes/"
	recipeNum = 0

	if not os.path.exists(path):
		os.mkdir(path,0o777)

	def parse(self, response):
		data = json.loads(response.body)

		for item in data.get('feed', []):
			link = "https://www.yummly.com/" + item.get("tracking-id")
			request = response.follow(link, callback=self.parseRecipe)
			yield request
	
	def parseRecipe(self, response):
		recipeName = response.css(".recipe-title::text").extract_first()
		ingredients = response.css(".ingredient::text").extract()
		ingredients = list(filter(Cleaning,ingredients))
		print("recipeName = ", recipeName)
		print(ingredients)

		self.recipeNum += 1
		fileName = self.path + str(self.recipeNum) + ".txt"
		outputFile= open(fileName, "w+")
		outputFile.write(str(recipeName) + "\n")
		for i in ingredients:
			outputFile.write(str(i) + "\n")
		outputFile.close()

			