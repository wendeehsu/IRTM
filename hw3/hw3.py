import re
import nltk
import operator
import math
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer 

stopwords = set(stopwords.words('english'))

def SetClass():
    f = open("training.txt", "r")
    trainDic = {}
    for line in f:
        rawList = line.replace("\n", "").split(' ')
        classId = 0
        for i in range(len(rawList)):
            if rawList[i] != '':
                if i == 0:
                    classId = int(rawList[i])
                    trainDic[classId] = []
                else:
                    trainDic[classId].append(rawList[i])
    return trainDic

def SetPrior(dic):
    prior = {}
    N = 0
    for i in range(1, classNum + 1):
        d_num = len(dic[i])
        N += d_num
        prior[i] = d_num
    
    for i in range(1, classNum + 1):
        prior[i] /= N
        
    return prior

def GetTerm(docId):
    f = open("../hw2/IRTM/" + str(docId) + ".txt", "r")
    text = f.read()

    text = text.replace("\n", " ")
    text = text.lower()
    regex = re.compile('[^a-zA-Z]')
    text = regex.sub(' ', text)
    tokens = text.split()

    terms = []
    for i in tokens:
        if i not in stopwords:
            terms.append(i)

    ps = PorterStemmer() 
    stemmedTerms = []
    word2tf = {}
    for i in terms:
        term = ps.stem(i)
        if term not in stemmedTerms:
            stemmedTerms.append(term)
            word2tf[term] = 1
        else:
            word2tf[term] += 1
    return word2tf, stemmedTerms

def GetId2Tf(dic):
    collectionTerms = []
    id2tf = {}   # {"documentID": {"term": tf}}
    for classId in range(1, classNum + 1):
        for docId in dic[classId]:  
            tfdic, terms = GetTerm(docId)
            id2tf[docId] = tfdic
            collectionTerms += terms
    return id2tf, list(set(collectionTerms))

def Getid2FeatureTFDic(dic):
    id2selectedTF = {}
    for docId in list(dic.keys()):
        selectedtf = {}
        for feature in features:
            if feature in dic[docId]:
                selectedtf[feature] = dic[docId][feature]
        id2selectedTF[docId] = selectedtf
    
    return id2selectedTF

def SelectFeature():
    # link ratio
    term2Class = {}
    for term in collectionTerms:
        class2df = {}
        for classId in range(1, classNum + 1):
            present = 0
            absent = 0
            for docId in trainDic[classId]:
                if term in id2tf[docId]:
                    present += 1
                else:
                    absent += 1
            class2df[classId] = {"present": present, "absent": absent}
        term2Class[term] = class2df

    featureScore = {}
    for chosenClassId in range(1, classNum + 1):
        term2score = {}
        for term in collectionTerms:
            onClassPresent = term2Class[term][chosenClassId]["present"]
            onClassAbsent = term2Class[term][chosenClassId]["absent"]
            outClassPresent = 0
            outClassAbsent = 0
            for classId in range(1, classNum + 1):
                if classId != chosenClassId:
                    outClassPresent += term2Class[term][classId]["present"]
                    outClassAbsent += term2Class[term][classId]["absent"]
            N = onClassPresent + onClassAbsent + outClassPresent + outClassAbsent
            pt = (onClassPresent + outClassPresent) / N
            p1 = onClassPresent / (onClassPresent + onClassAbsent)
            p2 = outClassPresent / (outClassPresent + outClassAbsent)
            upper = math.pow(pt,onClassPresent + outClassPresent) * math.pow(1-pt,onClassAbsent + outClassAbsent)
            lower = math.pow(p1,onClassPresent) * math.pow(1-p1,onClassAbsent) * math.pow(p2,outClassPresent) * math.pow(1-p2,outClassAbsent)
            score = -2 * math.log(upper/lower)
            term2score[term] = score
        
        sorted_ts = sorted(term2score.items(), key=operator.itemgetter(1))
        tfLength = len(sorted_ts)
        for i in range(tfLength-60,tfLength):
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

classNum = 13
trainDic = SetClass()
priorDic = SetPrior(trainDic)
id2tf, collectionTerms = GetId2Tf(trainDic)
features = SelectFeature()
id2selectedTF = Getid2FeatureTFDic(id2tf)

def GetConditionalProbability():
    feature2prob = {} # {"feature": {classNo: prob} }
    for feature in features:
        classProb = {}
        for classId in range(1, classNum + 1):
            totalTermTF = 0
            termTF = 0
            for docID in trainDic[classId]:
                totalTermTF += sum(id2selectedTF[docID].values())
                if feature in id2selectedTF[docID]:
                    termTF += id2selectedTF[docID][feature]
            prob = (termTF + 1) / (totalTermTF + 500)
            classProb[classId] = prob
        feature2prob[feature] = classProb
    
    return feature2prob

cp = GetConditionalProbability()

def Classify(docId):
    tfdic, terms = GetTerm(docId)
    choosenClass = -1
    maxScore = 0
    for classId in range(1, classNum + 1):
        score = priorDic[classId]
        for term in terms:
            if term in features:
                score *= math.pow(cp[term][classId], tfdic[term])
#         print("class ", classId, ", score = ", score)
        
        if score > maxScore:
            maxScore = score
            choosenClass = classId
#     print("chosen class = ", choosenClass, " with score = ", maxScore)
    
    return choosenClass

trainDocs = []
for classId in range(1, classNum + 1):
    trainDocs += trainDic[classId]

id2result = {} # {id: resultClass}
for i in range(1, 1095 + 1):
    if str(i) not in trainDocs:
        id2result[i] = Classify(i)

resultDF = pd.DataFrame.from_dict(id2result,orient='index',columns=["Value"])
resultDF.to_csv("result.csv")
