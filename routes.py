from flask import render_template
from flask import request
from flask import Flask
from tensorflow.keras.models import load_model
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

app = Flask(__name__)
@app.route('/index')
def index():
    return render_template('index.html', title='Home')
    
@app.route('/')
def x():
    return render_template('index.html', title='Home')

@app.route('/res/',methods=['POST','GET'])
def res():
	if request.method=='POST':
		model = load_model('model/model.h5')
		result = request.form['json_file']
		result = result[3:len(result)-3]
		result = ' '.join(result.split('%20'))
		x = result
		result = preprocess(result)
		i = model.predict_classes(result)[0]
		dept = labels[i]
		return render_template('1.html', name=dept, complaint=x)


if __name__ == "__main__":
    app.run(debug=True)
