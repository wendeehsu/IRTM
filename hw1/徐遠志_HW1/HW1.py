#!/usr/bin/env python
# coding: utf-8

# Requirement
# 1. Tokenization.
# 2. Lowercasing everything.
# 3. Stemming using Porter’s algorithm.
# 4. Stopword removal.
# 5. Save the result as a txt file

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer 

f = open("input", "r")
text = f.read()

# lower case + remove endl 
text = text.replace("\n", " ")
text = text.lower()

# remove non alphabatic characters
regex = re.compile('[^a-zA-Z]')
text = regex.sub(' ', text)

# Tokenization
tokens = text.split()

# remove stopwords
stopwords = set(stopwords.words('english'))
terms = []
for i in tokens:
    if i not in stopwords:
        terms.append(i)

# stemmimg
ps = PorterStemmer() 
stemmedTerms = []
for i in terms: 
    stemmedTerms.append(ps.stem(i))

# save result to text
outputFile= open("result.txt","w+")
for i in stemmedTerms:
    textwWithEndl = i + "\n"
    outputFile.write(textwWithEndl)
outputFile.close()
