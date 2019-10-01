from flask import Flask, render_template, redirect, url_for, request
from tensorflow.keras.models import load_model
from preprocess import vectorize
import numpy as np
import mysql.connector
import re
connection = mysql.connector.connect(host='localhost',
                                         database='syndicate',
                                         user='root',
                                         password='')

labels = ['Credit card',
 'Bank account',
 'Loan',
 'Debt collection',
 'Credit reporting',
 'Mortgage',
 'Debit card']

app = Flask(__name__)
session = {}

admins = ['admin0', 'admin1', 'admin2', 'admin3', 'admin4', 'admin5', 'admin6']

def add_complaint(complaint,did,uid):

    cursor = connection.cursor(buffered=True)
    print(did)
    query = 'UPDATE analysis SET issues = issues + 1 WHERE did = '+str(did)+';'
    cursor.execute(query)
    connection.commit()
    cursor.close()

    cursor = connection.cursor(buffered=True)
    q = 'SELECT * FROM complaint'
    result = cursor.execute(q)
    count = cursor.rowcount
    if len(complaint.split()) > 200:
        complaint = ' '.join(complaint.split()[0:200])
    query = 'INSERT INTO complaint VALUES('+str(count)+',"'+complaint+'",'+str(did)+',"'+uid+'", now(), "U", null);'
    cursor.execute(query)
    connection.commit()
    cursor.close()


def rem_complaint(cid):
    cursor = connection.cursor(buffered=True)
    query = 'DELETE FROM complaint WHERE cid = ' + str(cid)
    cursor.execute(q)
    connection.commit()
    cursor.close()

@app.route('/login', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        if session['username'] not in admins:
            return redirect(url_for('user'))
        else:
            user = session['username']
            user = int(''.join(list(filter(str.isdigit, user))))
            cursor = connection.cursor(buffered=True)
            q = 'SELECT * FROM complaint WHERE did = '+str(user)+';'
            cursor.execute(q)
            result = cursor.fetchall()
            cursor.close()
            complaint = []
            for x in result:
                row = []
                for elem in x:
                    row.append(elem)
                complaint.append(row)

            for i,c in enumerate(complaint):
                complaint[i][2] = labels[int(complaint[i][2])]
            return render_template('admin.html', dept=labels[user], complaints=complaint)
    if request.method == 'POST':
        session['username'] = request.form['username']

        if request.form['username'] not in admins:
            return redirect(url_for('user'))
        else:
            user = session['username']
            user = int(''.join(list(filter(str.isdigit, user))))
            cursor = connection.cursor(buffered=True)
            q = 'SELECT * FROM complaint WHERE did = '+str(user)+';'
            cursor.execute(q)
            result = cursor.fetchall()
            cursor.close()
            complaint = []
            for x in result:
                row = []
                for elem in x:
                    row.append(elem)
                complaint.append(row)

            for i,c in enumerate(complaint):
                complaint[i][2] = labels[int(complaint[i][2])]
            return render_template('admin.html', dept=labels[user], complaints=complaint)
    return render_template('login.html')

@app.route('/user', methods=['GET', 'POST'])
def user():
    if 'username' in session:
        if request.method=='POST':
            return redirect(url_for('logout'))
        u = session['username']
        cursor = connection.cursor(buffered=True)
        q = 'SELECT * FROM complaint WHERE uid = '+'"'+u+'";'
        cursor.execute(q)
        result = cursor.fetchall()
        cursor.close()
        complaint = []
        for x in result:
            row = []
            for elem in x:
                row.append(elem)
            complaint.append(row)

        for i,c in enumerate(complaint):
            complaint[i][2] = labels[int(complaint[i][2])]
        return render_template('user.html', title='Home', user=u, complaints = complaint)
    else:
        return redirect(url_for('login'))

@app.route('/new', methods = ['GET', 'POST'])
def new():
    return render_template('new.html')
@app.route('/res/',methods=['POST','GET'])
def res():
    if 'username' in session:
        if request.method=='POST':
            result = request.form['json_file']
            result = result[3:len(result)-3]
            result = re.sub('[^A-Za-z]+', ' ', result)
            x = result
            result = vectorize(result)
            model = load_model('static/model/new-model.h5')
            i = model.predict_classes(result)[0]
            dept = labels[i]
            user = session['username']
            add_complaint(x, i, user)
            return redirect(url_for('user'))
    else:
        return redirect(url_for('login'))



colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC"]

@app.route('/analysis/')
def analysis():
    query = 'SELECT issues, resolutions, misclassifications,diff from analysis WHERE did = {};'
    l = []
    issues = []
    resolutions = []
    for i in range(len(labels)):
        cursor = connection.cursor(buffered=True)
        cursor.execute(query.format(i))
        result = cursor.fetchall()
        print(result)
        l.append((i,labels[i],result[0][0],result[0][1],result[0][2], result[0][3]))
        issues.append(result[0][0])
        resolutions.append(result[0][1])
        cursor.close()
    return render_template('analysis.html', l = l, max=17000, set1=zip(issues, labels, colors), set2=zip(resolutions, labels, colors))

@app.route('/misclass/<int:c>', methods=['POST','GET'])
def misclass(c):
    if request.method == 'POST':
        x = request.form['dept']
        did = None
        for i,z in enumerate(labels):
            if z == x:
                did = i
                break
        q = 'SELECT did, resolved FROM complaint WHERE cid = '+str(c)+';'
        cursor = connection.cursor(buffered=True)
        cursor.execute(q)
        result = cursor.fetchall()
        cursor.close()
        print(result)
        if did != result[0][0] and result[0][1] != 'R':

            cursor = connection.cursor(buffered=True)
            print(did)
            query = 'UPDATE analysis SET issues = issues - 1 WHERE did = '+str(result[0][0])+';'
            cursor.execute(query)
            connection.commit()
            cursor.close()

            query = 'UPDATE analysis SET misclassifications = misclassifications+1 WHERE did = ' +str(result[0][0]) + ';'
            cursor = connection.cursor(buffered=True)
            cursor.execute(query)
            connection.commit()
            cursor.close()

            cursor = connection.cursor(buffered=True)
            print(did)
            query = 'UPDATE analysis SET issues = issues + 1 WHERE did = '+str(did)+';'
            cursor.execute(query)
            connection.commit()
            cursor.close()

            query = 'UPDATE complaint SET did = ' + str(did) + ' WHERE cid = ' +str(c) + ';'
            cursor = connection.cursor(buffered=True)
            cursor.execute(query)
            connection.commit()
            cursor.close()



    q = 'SELECT * FROM complaint WHERE cid = '+str(c)+';'
    cursor = connection.cursor(buffered=True)
    cursor.execute(q)
    result = cursor.fetchall()
    cursor.close()
    complaint = []
    for x in result:
        row = []
        for elem in x:
            row.append(elem)
        complaint.append(row)
    cursor.close()
    return render_template('misclass.html', departments = labels, complaints = complaint)

@app.route('/resolve/<int:c>', methods=['POST','GET'])
def resolve(c):
    cid = int(c)

    query = 'SELECT did,resolved FROM complaint WHERE cid = '+str(c)+';'
    cursor = connection.cursor(buffered=True)
    cursor.execute(query)
    did = cursor.fetchall()
    cursor.close()

    query = 'UPDATE analysis SET resolutions = resolutions + 1 WHERE did = ' + str(did[0][0])+ ' AND "' +str(did[0][1])+'" = "U";'
    cursor = connection.cursor(buffered=True)
    cursor.execute(query)
    connection.commit()
    cursor.close()


    query = 'UPDATE complaint SET end = now() WHERE cid = ' + str(c) + ';'
    cursor = connection.cursor(buffered=True)
    cursor.execute(query)
    connection.commit()
    cursor.close()

    query = 'SELECT date FROM complaint WHERE cid = '+str(c)+';'
    cursor = connection.cursor(buffered=True)
    cursor.execute(query)
    date = cursor.fetchall()
    cursor.close()

    query = 'SELECT datediff("'+str(date[0][0])+'",now());'
    cursor = connection.cursor(buffered=True)
    cursor.execute(query)
    diff = cursor.fetchall()
    cursor.close()

    query = 'UPDATE analysis SET diff = '+str(diff[0][0])+' WHERE did = ' + str(did[0][0])+ ' AND "' +str(did[0][1])+'" = "U";'
    cursor = connection.cursor(buffered=True)
    cursor.execute(query)
    connection.commit()
    cursor.close()

    query = 'UPDATE complaint SET resolved = "R" WHERE cid = ' + str(c) + ' AND "' +str(did[0][1])+'" = "U";'
    cursor = connection.cursor(buffered=True)
    cursor.execute(query)
    connection.commit()
    cursor.close()

    return redirect(url_for('login'))

@app.route('/unresolve/<int:c>', methods=['POST','GET'])
def unresolve(c):
    cid = int(c)

    query = 'SELECT did,resolved FROM complaint WHERE cid = '+str(c)+';'
    cursor = connection.cursor(buffered=True)
    cursor.execute(query)
    did = cursor.fetchall()
    cursor.close()

    query = 'UPDATE complaint SET date = now() WHERE cid = ' + str(c) + ' AND "'+str(did[0][1])+'" = "R";'
    cursor = connection.cursor(buffered=True)
    cursor.execute(query)
    connection.commit()
    cursor.close()

    query = 'UPDATE analysis SET resolutions = resolutions - 1 WHERE did = ' + str(did[0][0]) + ' AND resolutions>0 AND "'+str(did[0][1])+'" = "R";'
    cursor = connection.cursor(buffered=True)
    cursor.execute(query)
    connection.commit()
    cursor.close()

    query = 'UPDATE complaint SET resolved = "U" WHERE cid = ' + str(c) + ' AND resolved = "R";'
    cursor = connection.cursor(buffered=True)
    cursor.execute(query)
    connection.commit()
    cursor.close()
    return redirect(url_for('login'))

@app.route('/delete/<int:c>', methods=['POST','GET'])
def delete(c):
    cid = int(c)
    query = 'DELETE from complaint WHERE cid = ' + str(c) + ';'
    cursor = connection.cursor(buffered=True)
    cursor.execute(query)
    connection.commit()
    cursor.close()
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()

    return redirect(url_for('login'))

'''@app.route('/forum', methods = ['POST', 'GET'])
def forum():
    if request.method == 'POST':
        x = request.form['message']
        user = session['username']
    return render_template('forum.html')'''

if __name__ == "__main__":
    app.run(debug=True)
