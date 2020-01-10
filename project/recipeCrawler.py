import scrapy
import os
import json

def GenerateUrl(requiresRecipeNum):
	starts = []
	for i in range(requiresRecipeNum//10):
		apiStr = "https://mapi.yummly.com/mapi/v17/content/search?solr.seo_boost=new&start=" + str(1+i*10) + "&maxResult=10&fetchUserCollections=false&allowedContent=single_recipe&allowedContent=suggested_search&allowedContent=related_search&allowedContent=article&allowedContent=video&allowedContent=generic_cta&guided-search=true&solr.view_type=search_internal"
		starts += [apiStr]
	return starts

class RecipeSpider(scrapy.Spider):
	name = "recipe_spider"
	requiresRecipeNum = 10000
	start_urls = GenerateUrl(requiresRecipeNum)
	path = "recipes/"
	recipeNum = 0

	if not os.path.exists(path):
		os.mkdir(path,0o777)

	

	def parse(self, response):
		data = json.loads(response.body)

		for item in data.get('feed', []):
			link = "https://www.yummly.com/" + item.get("tracking-id")
			content = item.get('content')
			recipeName = content.get('details').get('name')

			self.recipeNum += 1
			fileName = self.path + str(self.recipeNum) + ".txt"
			outputFile= open(fileName, "w+")
			outputFile.write(str(recipeName) + "\n")
			outputFile.write(str(link) + "\n")

			for i in content.get('ingredientLines', []):
				outputFile.write(str(i.get('ingredient')) + "\n")
			
			outputFile.close()
			print(self.recipeNum," : ", recipeName)

		

			