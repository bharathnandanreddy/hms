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
                    return employee+"parama"
                elif(employee=="diagnostic"):
                    return employee+"diag"
                
            

    
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


@app.route('/accounts/', methods=['GET', 'POST'])
def searchAccount():
   
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
                
                if request.method == 'POST' and 'search' in request.form:
                    cid= request.form['search']
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    print(cid)
            
                    cursor.execute('select * from (SELECT account_status.acc_id ,account_status.cust_id ,account_status.status ,account_status.message ,account_status.last_updated,account.acc_type  FROM account_status,account WHERE account_status.acc_id=account.acc_id) as acc where  acc_id=%s or cust_id=%s;',(int(cid),int(cid),))
                    account = cursor.fetchall()

                    print('fecting',account)
                
                    if(account):
                        return  render_template('accounts.html',accounts=account)
            

    return redirect('/accounts')


@app.route('/patients/details/<int:pat_id>', methods=['GET', 'POST'])
def patientDetails(pat_id):
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                print('type',type(pat_id))
                cursor.execute('SELECT * FROM patient where pat_id= %s ', (int(pat_id),))
                account = cursor.fetchone()
                
                if(account):
                    print(account)
                    return  render_template('patientDetails.html',patient=account)
            

    return redirect('/')

@app.route('/accounts/details/<int:cid>', methods=['GET', 'POST'])
def accountDetails(cid):
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                print('type',type(cid))
                cursor.execute('SELECT * FROM account where acc_id= %s ', (int(cid),))
                account = cursor.fetchone()
                
                if(account):
                    print(account)
                    return  render_template('accountdetails.html',account=account)
            

    return redirect('/')



@app.route('/patients/createpatient', methods=['GET', 'POST'])
def createPatient():

    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
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


@app.route('/accounts/createaccount', methods=['GET', 'POST'])
def createAccount():

    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
                msg = ''
                if request.method == 'POST' and 'cust_id' in request.form and 'acc_type' in request.form and 'amount' in request.form :
                    cust_id = request.form['cust_id']
                    acc_type = request.form['acc_type']
                    amount = request.form['amount']
                    
                    # Check if customer exists already in database
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    # If account exists show error and validation checks

                                   
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    
                    cursor.execute('SELECT * FROM customer WHERE cust_id = %s', (cust_id,))
                    account = cursor.fetchone()
                    # If account exists show error and validation checks
                    if account:
                        # Account doesn't exist and form data is valid, insert into table
                        cursor.execute('INSERT INTO account(cust_id ,acc_type ,amount)VALUES(%s,%s, %s)', (cust_id, acc_type, amount))
                        mysql.connection.commit()
                        msg = 'Account record successfully created'
                        cursor.execute('select acc_id from account where cust_id = %s order by acc_id desc limit 1', (cust_id,))
                        acc_id=(cursor.fetchone())['acc_id']
                        ts = time.time()
                        print("cust id", cust_id)
                        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute('INSERT INTO account_status(acc_id ,cust_id ,status ,message ,last_updated)VALUES(%s,%s,%s,%s,%s  );', (acc_id, cust_id, "Active", msg, timestamp))
                        cursor.execute('INSERT INTO transactions(acc_id , amount, details, timestamp) VALUES(%s,%s,%s,%s);', (acc_id, amount, "Credit", timestamp))
                        mysql.connection.commit()
                    else:
                        msg="customer ID did not found.."
                        

                # Show registration form with message (if any)
                return render_template('createaccount.html', msg=msg)
                
                
            

    return redirect('/')

    

@app.route('/patients/updatepatient/<int:pat_id>', methods=['GET', 'POST'])
def updatePatient(pat_id):
    
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
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


@app.route('/accounts/<int:cid>', methods=['GET', 'POST'])
def deleteAccount(cid):
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('DELETE FROM account_status WHERE acc_id = %s',(cid,))
                mysql.connection.commit()
                msg = 'Account record successfully deleted'
                cursor.execute('DELETE FROM account WHERE acc_id = %s',(cid,))
                mysql.connection.commit()
                
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                
                cursor.execute('SELECT account_status.acc_id ,account_status.cust_id ,account_status.status ,account_status.message ,account_status.last_updated,account.acc_type  FROM account_status,account WHERE account_status.acc_id=account.acc_id;')
                account = cursor.fetchall()
               
                
                if(account):
                    return  render_template('accounts.html',accounts=account,msg=msg)
            
          
    
    return redirect('/')
@app.route('/deposit/<int:cid>', methods=['GET', 'POST'])
def deposit(cid):
    
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee !=True):
                if request.method == 'POST' and 'deposit_amount' in request.form :
                    msg=''
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('SELECT   * FROM account WHERE cust_id=%s and acc_id=%s',(session['cust_id'],cid))
                    account = cursor.fetchone()
                    if(account):
                        msg='Amount deposition successful'
                        if(int(request.form['deposit_amount'])>=1):
                            print(int(request.form['deposit_amount']),type(account['amount']))
                            account['amount']=int(request.form['deposit_amount'])+account['amount']
                            cursor.execute('UPDATE account SET amount = %s WHERE  acc_id = %s;',(account['amount'],cid))
                            ts = time.time()
                            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                            cursor.execute('INSERT INTO transactions(acc_id , amount, details, timestamp) VALUES(%s,%s,%s,%s);', (account['acc_id'], request.form['deposit_amount'], "Credit", timestamp))
                            mysql.connection.commit()
                        else:
                            msg='Invalid amount'
                        return render_template('deposit.html',account=account,msg=msg)
               
                else:
                    msg=''
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('SELECT   * FROM account WHERE cust_id=%s and acc_id=%s',(session['cust_id'],cid))
                    account = cursor.fetchone()
                    print(account)
                    
                    if(account):
                        return render_template('deposit.html',account=account,msg=msg)
               

    return redirect('/')
    
@app.route('/withdraw/<int:cid>', methods=['GET', 'POST'])
def withdraw(cid):
    
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee !=True):
                if request.method == 'POST' and 'deposit_amount' in request.form :
                    msg=''
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('SELECT   * FROM account WHERE cust_id=%s and acc_id=%s',(session['cust_id'],cid))
                    account = cursor.fetchone()
                    if(account):
                        msg='Amount withdrawal successful'
                        print(int(request.form['deposit_amount']),(account['amount']))
                        if(int(request.form['deposit_amount'])<=account['amount'] and  int(request.form['deposit_amount'])>=1 and  (account['amount'])>=1):
                            account['amount']=account['amount']-int(request.form['deposit_amount'])
                            cursor.execute('UPDATE account SET amount = %s WHERE  acc_id = %s;',(account['amount'],cid))
                            ts = time.time()
                            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                            cursor.execute('INSERT INTO transactions(acc_id , amount, details, timestamp) VALUES(%s,%s,%s,%s);', (account['acc_id'], request.form['deposit_amount'], "Debit", timestamp))
                            mysql.connection.commit()
                        else:
                            if(int(request.form['deposit_amount'])>account['amount']):
                                msg='insufficient funds'
                            else:
                                 msg= 'Invalid amount'
                        return render_template('withdraw.html',account=account,msg=msg)

                else:
                    msg=''
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('SELECT   * FROM account WHERE cust_id=%s and acc_id=%s',(session['cust_id'],cid))
                    account = cursor.fetchone()
                    print(account)
                    
                    if(account):
                        return render_template('withdraw.html',account=account,msg=msg)
               

    return redirect ('/')


@app.route('/transfer/<int:cid>', methods=['GET', 'POST'])
def transfer(cid):
    
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee !=True):
                if request.method == 'POST' and 'transfer_amount' in request.form and 'target_acc' in request.form and 'target_acc_type' in request.form :
                    msg=''
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('SELECT   * FROM account WHERE cust_id=%s and acc_id=%s',(session['cust_id'],cid))
                    account = cursor.fetchone()
                    if(account):
                        msg='Amount transfer successful'
                        
                        if(int(request.form['transfer_amount'])<=account['amount'] and  int(request.form['transfer_amount'])>=1 and  (account['amount'])>=1):
                            cursor.execute('SELECT   * FROM account WHERE acc_id=%s and acc_type=%s',(request.form['target_acc'],request.form['target_acc_type']))
                            target=cursor.fetchone()
                            if(target):
                                account['amount']=account['amount']-int(request.form['transfer_amount'])
                                target['amount']=target['amount']+int(request.form['transfer_amount'])
                                cursor.execute('UPDATE account SET amount = %s WHERE  acc_id = %s;',(account['amount'],cid))
                                cursor.execute('UPDATE account SET amount = %s WHERE  acc_id = %s;',(target['amount'],request.form['target_acc']))
                                ts = time.time()
                                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                                cursor.execute('INSERT INTO transactions(acc_id , amount, details, timestamp) VALUES(%s,%s,%s,%s);', (account['acc_id'], request.form['transfer_amount'], "Debit", timestamp))
                                cursor.execute('INSERT INTO transactions(acc_id , amount, details, timestamp) VALUES(%s,%s,%s,%s);', (target['acc_id'], request.form['transfer_amount'], "Credit", timestamp))
                                mysql.connection.commit()
                            else:
                                msg='Target account not found '

                            
                        else:
                            if(int(request.form['transfer_amount'])>account['amount']):
                                msg='insufficient funds'
                            else:
                                 msg= 'Invalid amount'
                        return render_template('transfer.html',account=account,msg=msg)

                else:
                    msg=''
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('SELECT   * FROM account WHERE cust_id=%s and acc_id=%s',(session['cust_id'],cid))
                    account = cursor.fetchone()
                    print(account)
                    
                    if(account):
                        return render_template('transfer.html',account=account,msg=msg)
               

    return redirect('/')

@app.route('/youraccounts', methods=['GET', 'POST'])
def yourAccounts():
        if(session):
            if(session["loggedin"]):
                global employee
                employee=session['employee']
                if(employee !=True):
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cust_id=session['cust_id']
                    cursor.execute('SELECT * FROM account where cust_id= %s ', (int(cust_id),))
                    accounts = cursor.fetchall()
                    
                    if(accounts):
                        print(accounts)
                        return  render_template('custAccountDetails.html', accounts=accounts)
        return redirect('/')

@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
        if(session):
            if(session["loggedin"]):
                global employee
                employee=session['employee']
                if(employee !=True):
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cust_id=session['cust_id']
                    cursor.execute('SELECT acc_id FROM account where cust_id= %s ', (int(cust_id),))
                    accounts = cursor.fetchall()
                    
                    if(accounts):
                        
                        if request.method == 'POST' and 'acc_number' in request.form and 'from' in request.form and 'to' in request.form :
                            acc_id=request.form['acc_number']
                            from_date = datetime.datetime.strptime(request.form['from'], "%Y-%m-%d")
                            to_date=datetime.datetime.strptime(request.form['to'], "%Y-%m-%d")+datetime.timedelta(days=1)
                           
                            cursor.execute('SELECT * FROM transactions where acc_id= %s and timestamp>=%s and timestamp<=%s', (int(acc_id),from_date,to_date))
                            trans = cursor.fetchall()
                            print(trans)
                            return  render_template('transactions.html', accounts=accounts, trans=trans)
                        
                        return  render_template('transactions.html', accounts=accounts )                                 
                
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)


