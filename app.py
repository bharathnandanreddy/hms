from flask import Flask, render_template , request, redirect, url_for, session
from flask_fontawesome import FontAwesome

from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import datetime 
import time




app = Flask(__name__)
fa = FontAwesome(app)
app.secret_key = 'secret_key_007'

# database connection details 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'manager'
app.config['MYSQL_PASSWORD'] = 'manager'
app.config['MYSQL_DB'] = 'hms'


mysql = MySQL(app)

employee=""




@app.route('/', methods=['GET', 'POST'])
def index():
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            print(session['userid'])
            cursor.execute('SELECT * FROM userstore WHERE user_id = %s', (session['userid'],))
            account = cursor.fetchone()
            if(account):
                if(employee=="admission"):
                    return  render_template('admissionHome.html')
                elif(employee=="pharmacist"):
                    return redirect('pharma')
                elif(employee=="diagnostic"):
                    return redirect('diagnostics')
                
            

    
    return render_template('index.html', msg='')





@app.route('/login', methods=['GET', 'POST'])
def login():
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            return   redirect('/')
            
  



    msg = ''

    print(request.form)

    if request.method == 'POST' and 'id' in request.form and 'password' in request.form:


        username = request.form['id']
        password = request.form['password']
      
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM userstore WHERE user_id = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists 
        if account:
            # Creating session data
            session['loggedin'] = True
            session['userid'] = account['user_id']
            employee=account['role']
            session['employee']= account['role']

            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            print(employee)
            cursor.execute('UPDATE userstore SET timestamp = %s WHERE  user_id = %s;',(timestamp,account['user_id']))
            mysql.connection.commit()
            return  redirect('/')
        else:
            # Account doesnt exist 
            msg = 'Incorrect username/password!!!'
        
        
    # Show the login form with message (if any)
    
    return render_template('index.html', msg=msg)



@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('cust_id', None)
    session.pop('employee', None)
    # Redirect to login page
    return redirect('/')



@app.route('/patients', methods=['GET', 'POST'])
def patients():
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee=="admission"):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                print(session['userid'])
                cursor.execute('SELECT * FROM patient where status=%s',('Active',))
                account = cursor.fetchall()
                
                if(account):
                    return render_template('patients.html',patients=account)
                else:
                    return render_template('patients.html', patients=account, msg='No patient details\n Click on Add customer to add patient details')
            

    return redirect('/')



@app.route('/patients/', methods=['GET', 'POST'])
def searchPatient():
   
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee=="admission"):
                
                if request.method == 'POST' and 'search' in request.form:
                    cid= request.form['search']
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    print(cid)
            
                    cursor.execute('select * from patient where ssn_id=%s or pat_id=%s;',(int(cid),int(cid),))
                    account = cursor.fetchall()

                    print('fecting',account)
                
                    if(account):
                        return  render_template('patients.html',patients=account)
            

    return redirect('/patients')





@app.route('/patients/details/<int:pat_id>', methods=['GET', 'POST'])
def patientDetails(pat_id):
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee=="admission"):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                print('type',type(pat_id))
                cursor.execute('SELECT * FROM patient where pat_id= %s ', (int(pat_id),))
                account = cursor.fetchone()
                
                if(account):
                    print(account)
                    return  render_template('patientDetails.html',patient=account)
            

    return redirect('/')




@app.route('/patients/createpatient', methods=['GET', 'POST'])
def createPatient():

    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee=="admission"):
                msg = ''
                if request.method == 'POST' and 'ssn_id' in request.form and 'pat_name' in request.form and 'age' in request.form and 'doj' in request.form and 'rtype' in request.form and 'address' in request.form and 'city' in request.form and 'state' in request.form:
                    ssn_id = request.form['ssn_id']
                    pat_name = request.form['pat_name']
                    age = request.form['age']
                    doj = request.form['doj']
                    rtype = request.form['rtype']
                    address = request.form['address']
                    city = request.form['city']
                    state = request.form['state']
                    # Check if patient exists already in database
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    # If account exists show error and validation checks
                    print(ssn_id)
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('SELECT * FROM patient WHERE ssn_id = %s', (ssn_id,))
                    account = cursor.fetchone()
                    # If account exists show error and validation checks
                    if account:
                        msg = 'Patient already exists with the same SSN ID!'
                    elif len(ssn_id)!=9:
                        msg = 'SSN ID should be 9 digits'
                    elif not re.match(r'[A-Za-z]+', pat_name):
                        msg = 'Patient Name must contain only characters'
                    elif not ssn_id or not pat_name:
                        msg = 'Please fill out the form!'
                    else:
                        # Account doesn't exist and form data is valid, insert into table
                        cursor.execute('INSERT INTO patient(ssn_id, pat_name, age, doj, rtype, address, city, state, status) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)', (ssn_id, pat_name, age, doj, rtype, address, city, state, "Active"))
                        mysql.connection.commit()
                        msg = 'Patient record created successfully'
                        

                # Show registration form with message (if any)
                return render_template('createpatient.html', msg=msg)
                
                
            

    return redirect('/')


@app.route('/patients/updatepatient/<int:pat_id>', methods=['GET', 'POST'])
def updatePatient(pat_id):
    
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee=="admission"):
                print(request.form)
                if request.method == 'POST' and 'ssn_id' in request.form and 'pat_name' in request.form and 'age' in request.form and 'doj' in request.form and 'rtype' in request.form and 'address' in request.form and 'city' in request.form and 'state' in request.form:
                    ssn_id = request.form['ssn_id']
                    pat_name = request.form['pat_name']
                    age = request.form['age']
                    doj = request.form['doj']
                    rtype = request.form['rtype']
                    address = request.form['address']
                    city = request.form['city']
                    state = request.form['state'] 
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    print('type',type(pat_id))
                    cursor.execute('UPDATE patient set pat_name=%s, age=%s, doj=%s, rtype=%s, address=%s, city=%s, state=%s WHERE pat_id= %s ', (pat_name, age, doj, rtype, address, city, state, int(pat_id)))
                    mysql.connection.commit()

                    cursor.execute('SELECT * FROM patient WHERE pat_id=%s', (pat_id, ))
                    account = cursor.fetchone()
                    return render_template('patientDetails.html',patient=account)
                else:
                    print('Form Incomplete')
            
          

    return redirect('/')

    


@app.route('/patients/<int:cid>', methods=['GET', 'POST'])
def deletePatient(cid):
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee=="admission"):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

                cursor.execute('DELETE FROM patient WHERE pat_id = %s',(cid,))
                mysql.connection.commit()
                msg = 'Account record successfully deleted'
                print(session['userid'])
                cursor.execute('SELECT * FROM patient')
                account = cursor.fetchall()
                
                if(account):
                    return render_template('patients.html', patients=account, msg=msg)
            
          
    
    return redirect('/')




@app.route('/pharma', methods=['GET', 'POST'])
def pharma():
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee=="pharmacist"):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                print(session['userid'])
                cursor.execute('SELECT * FROM patient where status=%s',('Active',))
                account = cursor.fetchall()
                
                if(account):
                    return render_template('pharmaHome.html',patients=account)
                else:
                    return render_template('pharmaHome.html', patients=account, msg='No patient details')
            

    return redirect('/')



@app.route('/pharma/', methods=['GET', 'POST'])
def searchPharmaPatient():
    
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee=="pharmacist"):
                if request.method == 'POST' and 'search' in request.form:
                    cid= request.form['search']
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    print(cid)
            
                    cursor.execute('select * from patient where ssn_id=%s or pat_id=%s;',(int(cid),int(cid),))
                    account = cursor.fetchall()

                    print('fetching',account)
                
                    if(account):
                        return  render_template('pharmaHome.html',patients=account)
                else:
                    return redirect("/pharma")
            

    return redirect('/')





@app.route('/pharma/details/<int:pat_id>', methods=['GET', 'POST'])
def pharmaPatientDetails(pat_id):
    print('entered')
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee=="pharmacist"):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                print('type',type(pat_id))
                cursor.execute('SELECT * FROM patient where pat_id= %s ', (int(pat_id),))
                account = cursor.fetchone()
                cursor.execute('SELECT * FROM medicines_issued where pat_id= %s ', (int(pat_id),))
                medicines=cursor.fetchall()
                
                if(account):
                    print(account)
                    return  render_template('pharmaPatientDetails.html',patient=account,medicines=medicines)
            

    return redirect('/')
    
    

@app.route('/issueMed/<int:pat_id>', methods=['GET', 'POST'])
def issueMed(pat_id):
    
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM medicines')
            medicines = cursor.fetchall()
            

            if(employee=="pharmacist"):
                if request.method == 'POST' and 'med_name' in request.form and 'rate' in request.form and 'quantity_issued' in request.form:
                    
                    med_name=request.form['med_name']
                    quantity_issued=request.form['quantity_issued']
                    rate=request.form['rate']
                    print(med_name,rate,quantity_issued,pat_id)

                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute("SELECT * FROM medicines WHERE med_name = %s", (med_name,))
                    medicine = cursor.fetchone()
                    med_id = medicine['med_id']
                    quantity = medicine['quantity']
                    if(int(quantity_issued) <= quantity):
                        cursor.execute("INSERT INTO medicines_issued(pat_id, med_id, med_name, quantity_issued, med_rate, amount) values (%s, %s, %s, %s, %s, %s)", (pat_id, med_id, med_name, quantity_issued, rate, int(quantity_issued)*int(rate)))
                        mysql.connection.commit()
                        cursor.execute("UPDATE medicines SET quantity = %s WHERE med_id=%s",(quantity-int(quantity_issued),med_id))
                        mysql.connection.commit()
                        return render_template('issueMed.html',medicines=medicines,pat_id=pat_id,msg="Medicines issued successfully")
                    else:
                        return render_template('issueMed.html',medicines=medicines,pat_id=pat_id,msg="Quantity unavailable")

                else:

                    return render_template('issueMed.html',medicines=medicines,pat_id=pat_id)
            

    return redirect('/')


@app.route('/diagnostics', methods=['GET', 'POST'])
def diagnostics():
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee=="diagnostic"):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                print(session['userid'])
                cursor.execute('SELECT * FROM patient where status=%s',('Active',))
                account = cursor.fetchall()
                
                if(account):
                    return render_template('diagnosticsHome.html',patients=account)
                else:
                    return render_template('diagnosticsHome.html', patients=account, msg='No patient details')
            

    return redirect('/')


@app.route('/diagnostics/', methods=['GET', 'POST'])
def searchDiagnosticsPatient():
    
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee=="diagnostic"):
                if request.method == 'POST' and 'search' in request.form:
                    cid= request.form['search']
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    print(cid)
            
                    cursor.execute('select * from patient where ssn_id=%s or pat_id=%s;',(int(cid),int(cid),))
                    account = cursor.fetchall()

                    print('fetching',account)
                
                    if(account):
                        return  render_template('diagnosticsHome.html',patients=account)
                else:
                    return redirect("/diagnostics")
            

    return redirect('/')


@app.route('/diagnostics/details/<int:pat_id>', methods=['GET', 'POST'])
def diagnosticsPatientDetails(pat_id):
    print('entered')
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee=="diagnostic"):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                print('type',type(pat_id))
                cursor.execute('SELECT * FROM patient where pat_id= %s ', (int(pat_id),))
                account = cursor.fetchone()
                cursor.execute('SELECT * FROM diagnostics_conducted where pat_id= %s ', (int(pat_id),))
                tests=cursor.fetchall()
                
                if(account):
                    print(account)
                    return  render_template('diagnosticsPatientDetails.html',patient=account,tests=tests)
            

    return redirect('/')


@app.route('/conductDiagnostics/<int:pat_id>', methods=['GET', 'POST'])
def conductDiagnostics(pat_id):
    
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM diagnostics')
            tests = cursor.fetchall()
            

            if(employee=="diagnostic"):
                if request.method == 'POST' and 'test_name' in request.form and 'rate' in request.form:
                    
                    test_name=request.form['test_name']
                    test_rate=request.form['rate']
                    print(test_name,test_rate,pat_id)

                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute("SELECT * FROM diagnostics WHERE test_name = %s", (test_name,))
                    test = cursor.fetchone()
                    test_id = test['test_id']
                    cursor.execute("INSERT INTO diagnostics_conducted(pat_id, test_id, test_name, test_rate) values (%s, %s, %s, %s)", (pat_id, test_id, test_name, test_rate))
                    mysql.connection.commit()

                
                    if(tests):
                        return render_template('conductDiagnostics.html',tests=tests, pat_id=pat_id,msg="Test added successfully")
                else:

                    return render_template('conductDiagnostics.html',tests=tests, pat_id=pat_id)
            

    return redirect('/')


@app.route('/billing', methods=['GET', 'POST'])
def billing():
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee=="admission"):
                account={"ssn_id":"", "pat_id":0, "pat_name":"", "age":"","dod":"", "doj":"", "rtype":"", "address":"", "city":"", "state":"", "status":"","roombill":""}
                med_sum=0
                dig_sum=0
                medicines=[]
                tests=[]
                msg=""

                if(request.method=='POST' and 'confirm_pid' in request.form):
                    pat_id=request.form['confirm_pid']
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    print(int(pat_id))
                    cursor.execute('UPDATE patient set status=%s WHERE pat_id= %s ', ("Discharged", int(pat_id)))
                    mysql.connection.commit()
                    msg="Payment Successfully"

                
                if request.method == 'POST' and 'pat_id' in request.form :
                    pat_id=request.form['pat_id']
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    print('type',type(pat_id))
                    cursor.execute('SELECT * FROM patient where pat_id= %s and status=%s', (int(pat_id),'Active'))
                    account = cursor.fetchone()
                    if(account):
                        ts = time.time()
                        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                        account["dod"]=timestamp
                        diff=datetime.datetime.fromtimestamp(ts).date()-account["doj"]
                        print("diff",diff.days)
                        if(account["rtype"]=="Semi"):
                            account["roombill"]=4000*diff.days
                        if(account["rtype"]=="Single"):
                            account["roombill"]=8000*diff.days
                        if(account["rtype"]=="General"):
                            account["roombill"]= 2000*diff.days
                        print( account["roombill"])

                        cursor.execute('SELECT * FROM medicines_issued where pat_id= %s', (int(pat_id),))
                        medicines=cursor.fetchall()
                        
                        

                        for med in medicines:
                            med_sum+=med['amount']
                        
                        cursor.execute('SELECT * FROM diagnostics_conducted where pat_id= %s ', (int(pat_id),))
                        tests=cursor.fetchall()
                        for test in tests:
                            dig_sum+=test['test_rate']

                        grand_tot=account["roombill"]+med_sum+dig_sum
                     
                        print(account)
                        return  render_template('billing.html',patient=account,medicines=medicines,med_sum=med_sum,dig_sum=dig_sum,tests=tests,grand_tot=grand_tot)
                    else:
                        return  render_template('billing.html',patient=account,medicines=medicines,med_sum=med_sum,dig_sum=dig_sum,tests=tests,msg="Invalid patient")
                else:
                    print(account)
                    return render_template('billing.html',patient=account,medicines=medicines,med_sum=med_sum,dig_sum=dig_sum,tests=tests,msg=msg)

            

    return redirect('/')





if __name__ == '__main__':
    app.run(debug=True)