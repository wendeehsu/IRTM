import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer 
import math
import copy
import numpy as np
import pickle

class Node(object):
    def __init__(self):
        self.index = 0
        self.cos = 0
        
    def __init__(self, index, cos):
        self.index = index
        self.cos = cos
        
    def peek(self):
        print("(" + str(self.index) + "," + str(self.cos) + ")")

class MaxHeap(object):
    def __init__(self):
        self.arr = [Node(0,0)] # first node is unused
        self.count = 0
    
    def getMax(self):
        if self.count > 0:
            return self.arr[1]
        return False
    
    def getAll(self):
        for i in self.arr[1:]:
            i.peek()
    
    def shiftUp(self, node, pos):
        if pos > 1:
            parent = self.arr[pos//2]
            if parent.cos < node.cos:
                self.arr[pos//2], self.arr[pos] = node, self.arr[pos//2]
                self.shiftUp(node,pos//2)
                
    def push(self, node):
        self.arr.append(node)
        self.count += 1
        self.shiftUp(node, self.count)
    
    def getNode(self, index):
        for i,node in enumerate(self.arr):
            if node.index == index and i != 0:
                return i,node
        print("node not found")
        return False
    
    def shiftDown(self, node, pos):
        if pos*2 <= self.count: # left tree
            minIndex = pos*2
            minNode = self.arr[minIndex]
            if (minIndex+1) <= self.count and minNode.cos < self.arr[minIndex+1].cos:
                minIndex = minIndex + 1
                minNode = self.arr[minIndex]
            
            if node.cos < minNode.cos:
                self.arr[pos] , self.arr[minIndex] = minNode, node
                self.shiftDown(node,minIndex)
    
    def pop(self, docIndex):
        index, node = self.getNode(docIndex)
        if index != self.count:
            self.arr[index], self.arr[self.count] = self.arr[self.count], node
        del self.arr[self.count]
        self.count -= 1
        if index < self.count:
            self.shiftDown(self.arr[index],index)
        
    def update(self, node):
        self.pop(node.index)
        self.push(node)


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
vectors = [0]
for i in range(1,docSize + 1):
    vectors.append(GetVector(id2word[i]))

sampleSize = docSize  # change to docSize when we are ready to run
def SetMatrix():
    simMatrix = np.zeros(shape=(sampleSize,sampleSize))
    for i in range(sampleSize):
        for j in range(i):
            simMatrix[i][j] = cosine(vectors[i],vectors[j])

    return simMatrix

def SetHeap():
    heapDic = {}
    for i in range(1,sampleSize+1):
        heap = MaxHeap()
        for j in range(1,sampleSize+1):
            if i != j:
                cos = cosine(vectors[i],vectors[j])
                heap.push(Node(j,cos))
        heapDic[i] = heap
        # print("i = ", i)
        # heap.getAll()

    return heapDic


def FindMaxSim(heaps, availList):
    maxSim = -1
    maxPair = (-1,-1)
    
    for i in list(heaps.keys()):
        candidateNode = heaps[i].getMax()
        if candidateNode.cos > maxSim and availList[i] == 1 and availList[candidateNode.index] == 1:
            maxSim = candidateNode.cos
            maxPair = (i,candidateNode.index)
            if i < candidateNode.index:
                maxPair = (candidateNode.index,i)

    return maxPair

def updateHeap(heapDic,pair): # pair = (大,小)
    keys = list(heapDic.keys())
    heap_update = MaxHeap()
    for i in keys:
        if i != pair[0] and i != pair[1]:
            index_update, node_update = heapDic[i].getNode(pair[1])
            index_rm, node_rm = heapDic[i].getNode(pair[0])

            if node_update.cos > node_rm.cos:
                node_update.cos = node_rm.cos

            heapDic[i].pop(pair[0])
            heapDic[i].update(node_update)
            heap_update.push(Node(i,node_update.cos))

    heapDic[pair[1]] = heap_update
    del heapDic[pair[0]]

    heapDic[pair[1]].getAll()

    return heapDic

def InitClusters():
    dic = {}
    for i in range(1, sampleSize+1):
        dic[i] = [i]
    return dic

def updateCluster(dic,pair):  # pair = (大,小)
    dic[pair[1]] += dic[pair[0]]
    del dic[pair[0]]

    return dic
        
def HAC():
    availability = [0] + [1] * sampleSize
    log = {} # {clusterAmout : list of clusters}
    heapDic = SetHeap()
    clusters = InitClusters()
    
    clusterAmount = sampleSize
    while clusterAmount > 1 :
        print("clusterAmount = ", clusterAmount)
        mergePair = FindMaxSim(heapDic, availability)
        print("mergePair: ", mergePair)
        availability[mergePair[0]] = 0
        heapDic = updateHeap(heapDic, mergePair)
        clusters = updateCluster(clusters,mergePair)
        clusterAmount -= 1
        log[clusterAmount] = copy.deepcopy(clusters)
    
    return log

hacLog = HAC()
# print("==== hacLog ====")
# print(hacLog)
hacLogFile = open('hacLog.pkl', 'wb') 
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
