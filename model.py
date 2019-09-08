from tensorflow.keras.models import load_model
import tensorflow as tf
import keras
from preprocessing import preprocess
import numpy as np

labels = ['Bank account or service',
 'Consumer Loan',
 'Credit card',
 'Credit reporting',
 'Debt collection',
 'Money transfers',
 'Mortgage',
 'Other financial service',
 'Payday loan',
 'Prepaid card',
 'Student loan']
 
model = load_model('model/model2.h5')

def predict(x):
    x = preprocess(x)
    x = np.asarray(x).reshape(1,50)
    i = model.predict_classes(x)[0]
    return labels[i]
    

