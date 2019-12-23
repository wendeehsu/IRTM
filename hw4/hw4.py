import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer 
import math
import pandas as pd
import copy
import numpy as np

docSize = 1095
stopwords = set(stopwords.words('english'))

def GetTerm(fileName):
    f = open(fileName, "r")
    text = f.read()

    text = text.replace("\n", " ")
    text = text.lower()
    regex = re.compile('[^a-zA-Z]')
    text = regex.sub(' ', text)
    tokens = text.split()

    # remove stopwords
    terms = []
    for i in tokens:
        if i not in stopwords:
            terms.append(i)

    # stemmimg
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

id2word = {}   # {"document id" : {"term" : "term frequency"}}
df = {}        # {"term" : "df"}

# Get df and set each document's term tf
for i in range(1,docSize + 1):
    dic, terms = GetTerm("../hw2/IRTM/" + str(i) + ".txt")
    id2word[i] = dic
    for term in terms:
        if term in df:
            df[term] += 1
        else:
            df[term] = 1

dictTerms = list(df.keys())

def GetTFiDF(tf,term):
    termDf = df[term]
    idf = math.log((docSize/termDf),10)
    return tf * idf

def GetVector(tfDic):
    vector = []
    for term in dictTerms:
        if term in tfDic:
            vector.append(GetTFiDF(tfDic[term],term))
        else:
            vector.append(0)
    vectorLen = sum(vector)
    normalizedVec = list(map(lambda x: x/vectorLen, vector))
    
    return np.array(normalizedVec)

def cosine(v1,v2):
    upper = np.sum(v1*v2)
    lower1 = np.sum(v1*v1) ** 0.5
    lower2 = np.sum(v2*v2) ** 0.5
    return upper/(lower1*lower2)

# make tfidf vector
vectors = []
for i in range(1,docSize + 1):
    vectors.append(GetVector(id2word[i]))

sampleSize = docSize  # change to docSize when we are ready to run
def SetMatrix():
    simMatrix = np.zeros(shape=(sampleSize,sampleSize))
    for i in range(sampleSize):
        for j in range(i):
            simMatrix[i][j] = cosine(vectors[i],vectors[j])

    return simMatrix

def FindMaxSim(matrix, availList):
    maxSim = -1
    maxPair = (-1,-1)
    
    for i in range(sampleSize):
        for j in range(i):
            if matrix[i][j] > maxSim and availList[i] == 1 and availList[j] == 1:
                maxSim = matrix[i][j]
                maxPair = (i,j)
    return maxPair

def updateMatrix(matrix,pair): # pair = (大,小)
    # horizontal
    for i in range(pair[1]):
        newValue = min(matrix[pair[0]][i], matrix[pair[1]][i])
        matrix[pair[1]][i] = newValue
    
    # vertical
    for j in range(pair[1]+1, sampleSize):
        if j != pair[0]:
            if j < pair[0] and j > pair[1]:
                newValue = min(matrix[j][pair[1]], matrix[pair[0]][j])
                matrix[j][pair[1]] = newValue
            else:
                newValue = min(matrix[j][pair[1]], matrix[j][pair[0]])
                matrix[j][pair[1]] = newValue
            
    return matrix

def InitClusters():
    dic = {}
    for i in range(1, sampleSize+1):
        dic[i] = [i]
    return dic

def updateCluster(dic,pair):  # pair = (大,小)
    dic[pair[1] + 1] += dic[pair[0] + 1]
    del dic[pair[0] + 1]

    return dic
        
def HAC():
    availability = [1] * sampleSize
    log = {} # {clusterAmout : list of clusters}
    simMatrix = SetMatrix()
    clusters = InitClusters()
    
    clusterAmount = sampleSize
    while clusterAmount > 1 :
        print("clusterAmount = ", clusterAmount)
        mergePair = FindMaxSim(simMatrix, availability)
        print("mergePair: ", mergePair)
        availability[mergePair[0]] = 0
        simMatrix = updateMatrix(simMatrix, mergePair)
        clusters = updateCluster(clusters,mergePair)
        clusterAmount -= 1
        log[clusterAmount] = copy.deepcopy(clusters)
    
    return log
    
hacLog = HAC()
hacLogFile = open('hacLog.pkl', 'ab') 
pickle.dump(hacLog, hacLogFile)

def SaveCluster(num):
    fileName = str(num) + ".txt"
    outputFile= open(fileName,"w+")
    for clusterID in list(hacLog[num].keys()):
        rawArray = np.array(hacLog[num][clusterID])
        arr = np.sort(rawArray)
        for i in arr:
            outputFile.write(str(i) + "\n")
        outputFile.write("\n")
    outputFile.close()

SaveCluster(8)
SaveCluster(13)
SaveCluster(20)
