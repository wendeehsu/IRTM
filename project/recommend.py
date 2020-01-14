import nltk
import json
import pickle
import math
import operator
from nltk.stem import WordNetLemmatizer 

lemmatizer = WordNetLemmatizer()
ingredientList = []

with open('ingredientList.pickle', 'rb') as f:
	ingredientList = pickle.load(f)

def Normalize(ingrediant):
	ingrediant = ingrediant.lower()
	ingrediants = ingrediant.split()
	ingrediants = list(map(lambda i : lemmatizer.lemmatize(i), ingrediants)) 
	return " ".join(ingrediants)

def GetIngredient(ingredient):
	global ingredientList
	ingredient = Normalize(ingredient)
	if ingredient not in ingredientList:
		details = ingredient.split()
		if len(details) == 1:
			return ingredient
		else:
			for i in ingredientList:
				for detail in details:
					if i == detail:
						return i
	return ingredient

def GetTerm(docId):
	f = open("recipes/" + str(docId) + ".txt", "r")
	text = f.read()
	ingrediants = text.split("\n")[2:]
	ingrediants.pop()
	ingrediants = list(map(GetIngredient,ingrediants))
	
	return list(set(ingrediants))

def SetPrior():
	prior = {}
	with open('train.json') as json_file:
		data = json.load(json_file)
		N = len(data)
		for index,element in enumerate(data):
			if element["cuisine"] not in prior:
				prior[element["cuisine"]] = 1
			else:
				prior[element["cuisine"]] += 1
		
		for i in prior:
			prior[i] /= N

	return prior

def GetTotalDF():
	global ingredientList
	trainData = []
	with open('train.json') as json_file:
		trainData = json.load(json_file)

	# normalize training data
	for doc in trainData:
		doc["ingredients"] = list(map(GetIngredient, doc["ingredients"]))

	term2TotalNum = {}
	for term in ingredientList:
		term2TotalNum[term] = 0
		for doc in trainData:
			if term in doc["ingredients"]:
				term2TotalNum[term] += 1
	return trainData, term2TotalNum

def SelectFeatures():
	global ingredientList, categoryList, trainData, term2TotalNum

	# link ratio
	term2Class = {}
	for term in ingredientList:
		class2df = {}
		for className in categoryList:
			present = 0
			absent = 0
			for doc in trainData:
				if doc["cuisine"] == className:
					if term in doc["ingredients"]:
						present += 1
					else:
						absent += 1
			class2df[className] = {"present": present, "absent": absent}
		term2Class[term] = class2df

	featureScore = {}
	N = len(trainData)
	termAmount = len(ingredientList)
	
	for chosenClassName in categoryList:
		term2score = {}
		for term in ingredientList:
			onClassPresent = term2Class[term][chosenClassName]["present"]
			onClassAbsent = term2Class[term][chosenClassName]["absent"]
			outClassPresent = term2TotalNum[term] - onClassPresent
			outClassAbsent = N - onClassPresent - onClassAbsent - outClassPresent
			pt = term2TotalNum[term] / N
			p1 = onClassPresent / (onClassPresent + onClassAbsent)
			p2 = outClassPresent / (outClassPresent + outClassAbsent)
			upper = math.pow(pt,term2TotalNum[term]) * math.pow(1-pt,onClassAbsent + outClassAbsent)
			lower = math.pow(p1,onClassPresent) * math.pow(1-p1,onClassAbsent) * math.pow(p2,outClassPresent) * math.pow(1-p2,outClassAbsent)
			if lower == 0 or upper == 0:
				term2score[term] = 0
			else:
				term2score[term] = -2 * math.log(upper/lower)
		
		sorted_ts = sorted(term2score.items(), key=operator.itemgetter(1))
		for i in range(termAmount-30,termAmount):
			if sorted_ts[i][0] in featureScore:
				if sorted_ts[i][1] > featureScore[sorted_ts[i][0]]:
					featureScore[sorted_ts[i][0]] = sorted_ts[i][1]
			else:
				featureScore[sorted_ts[i][0]] = sorted_ts[i][1]
	
	sorted_feature = sorted(featureScore.items(), key=operator.itemgetter(1))
	sfLength = len(sorted_feature)
	selectedFeature = []
	for i in range(sfLength-500,sfLength):
		selectedFeature.append(sorted_feature[i][0])
		
	return selectedFeature

def GetConditionalProbability():
	global features, categoryList, trainData, term2TotalNum
	feature2prob = {} 		# {"feature": {classNo: prob} }
	for feature in features:
		classProb = {}
		for className in categoryList:
			totalTermTF = 0
			termTF = 0
			for doc in trainData:
				if doc["cuisine"] == className:
					totalTermTF += len(doc["ingredients"])
					if feature in doc["ingredients"]:
						termTF += doc["ingredients"].count(feature)
			prob = (termTF + 1) / (totalTermTF + 500)
			classProb[className] = prob
		feature2prob[feature] = classProb
	
	return feature2prob

def Classify(docId):
	global categoryList, cp
	global features
	terms = GetTerm(docId)
	choosenClass = -1
	maxScore = 0
	for className in categoryList:
		score = priorDic[className]
		for term in terms:
			if term in features:
				score *= math.pow(cp[term][classId], tfdic[term])
		print("class ", classId, ", score = ", score)
		
		if score > maxScore:
			maxScore = score
			choosenClass = classId
	print("chosen class = ", choosenClass, " with score = ", maxScore)
	
	return choosenClass

priorDic = SetPrior()
categoryList = list(priorDic.keys())
trainData, term2TotalNum = GetTotalDF()
features = SelectFeatures()
cp = GetConditionalProbability()
print("====================")
print(features)

# with open("features.pickle", "wb") as f:
# 	pickle.dump(features, f)

# Classify(1)




# imput_ingredients = input("imgredients : ").split(",")
# intended_type = input("type : ")
# imput_ingredients = list(map(Normalize, imput_ingredients))
# intended_type = lemmatizer.lemmatize(intended_type)
# print(imput_ingredients)