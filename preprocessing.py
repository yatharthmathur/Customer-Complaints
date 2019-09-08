import numpy as np
import nltk
from nltk.corpus import stopwords
stopword = set(stopwords.words('english'))
from nltk import word_tokenize
import re
from itertools import chain
from gensim.models import Word2Vec
from joblib import load, dump

embedding = Word2Vec.load('w2v_embedding.model')
print(embedding)
transformer = load('PCA.joblib')
print(transformer)
def preprocess(x):
    x = x.lower()
    x = re.sub(r'[^\w]', ' ', x)
    x = word_tokenize(x)
    x = [w for w in x if w not in stopword]
    if len(x) > 50:
        x = x[:50]
    for j in range(50-len(x)):
            x.append(' ')

    for i, word in enumerate(x):
        if word in embedding.wv.vocab.keys():
            x[i] = embedding[word]
        else:
            x[i] = [0]*50
    x = list(chain.from_iterable(x))
    x = np.asarray(x).reshape(1, len(x))
    x = transformer.transform(x)

    return x
