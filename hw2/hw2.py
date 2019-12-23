# # TODO:
# 1. Construct a dictionary based on the terms extracted from the given documents.
# 2. Record the document frequency of each term. (save "dictionary.txt")
# 3. Transfer each document into a tf-idf unit vector.
# 4. Write a function cosine(Docx, Docy) which loads the tf-idf vectors of documents x and y and returns their cosine similarity.

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer 
import math
import pandas as pd

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
    dic, terms = GetTerm("IRTM/" + str(i) + ".txt")
    id2word[i] = dic
    for term in terms:
        if term in df:
            df[term] += 1
        else:
            df[term] = 1

# save df as csv file
dfDataFrame = pd.DataFrame.from_dict(df, orient='index',columns=["df"])
dfDataFrame = dfDataFrame.sort_values('df')
dfDataFrame.reset_index(level=0, inplace=True)
dfDataFrame.columns = ["term","df"]
dfDataFrame.index += 1
dfDataFrame.to_csv("dictionary.csv")

dictTerms = dfDataFrame['term'].tolist()

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
    
    return vector

# make tfidf vector
vectors = []
for i in range(1,docSize + 1):
    vectors.append(GetVector(id2word[i]))

# save vector of 1.txt to text
outputFile= open("vector1.txt","w+")
outputFile.write(str(len(id2word[1])) + "\n")
outputFile.write("t_index   tf-idf \n")
for index, point in enumerate(vectors[0]):
    if point != 0 :
        outputFile.write(str(index+1) + "   " + str(point) + "\n")
outputFile.close()

def cosine(v1,v2):
    upper = sum(list(map(lambda x,y: x*y, v1, v2)))
    lower1 = (sum(list(map(lambda x: x**2, v1)))) ** 0.5
    lower2 = (sum(list(map(lambda x: x**2, v2)))) ** 0.5
    return upper/(lower1*lower2)

print(cosine(vectors[0],vectors[1]))

