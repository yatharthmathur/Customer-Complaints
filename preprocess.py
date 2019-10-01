
import gensim
import numpy as np
from gensim import corpora
# Preprocesses a string
from gensim.utils import simple_preprocess

# Stop words set
from nltk.corpus import stopwords
# Lematize Words
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
#Constants
from gensim.models import Phrases, Word2Vec
unique_labels = ['Credit card',
 'Bank account',
 'Loan',
 'Debt collection',
 'Credit reporting',
 'Mortgage',
 'Debit card']


bigram_path = 'static/model/bigram_mod'
trigram_path = 'static/model/trigram_mod'
word2vec_path = 'static/model/w2v.model'
stop_words = set(stopwords.words('english'))
vector_length = 20
max_len = 50
lem = WordNetLemmatizer()
bigram_mod = Phrases.load(bigram_path)
trigram_mod = Phrases.load(trigram_path)
w2v_model = Word2Vec.load(word2vec_path)
word_vectors = w2v_model.wv
# Extend the stopwords list
stop_words.update(['xxxx', 'xxxxxxx', 'xxxxxxxxxxxx'])
trigram = lambda tokens: trigram_mod[bigram_mod[tokens]]
remove_stopw = lambda x: [w for w in x if w not in stop_words]
get_lem = lambda token: [lem.lemmatize(w) for w in token]
tags_to_keep = ['JJ', 'NN', 'VB', 'NNS']
pos = lambda token: [w[0] for w in token if w[1] in tags_to_keep]
def len_adjust(x):
    while len(x) < max_len:
        x.append(' ')
    if len(x) > max_len:
        x = x[0:max_len]
    return x

def convert(x):
    for j,w in enumerate(x):
        if w not in word_vectors.vocab:
            x[j] = np.asarray([0]*vector_length, dtype='float32')
        else:
            x[j] = w2v_model[x[j]]
    return x

def vectorize(x):
    data = simple_preprocess(x, True, 3)
    data = remove_stopw(data)
    data = trigram(data)
    data = get_lem(data)
    data = pos_tag(data)
    data = pos(data)
    data = len_adjust(data)
    data = convert(data)
    data = np.asarray(data).reshape((1, max_len, vector_length, 1))
    return data
