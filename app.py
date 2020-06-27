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
app.config['MYSQL_DB'] = 'bms'


mysql = MySQL(app)
employee=False
user_view="Account/SSN/Customer-ID "
empVisible=""
custVisible="active"

@app.route('/', methods=['GET', 'POST'])
def index():
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                print(session['userid'])
                cursor.execute('SELECT * FROM employee WHERE user_id = %s', (session['userid'],))
                account = cursor.fetchone()
                if(account):
                    return  render_template('empHome.html',empname=account['emp_name'])
            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                print(session['cust_id'])
                cursor.execute('SELECT customer.cust_name, account.acc_id FROM customer,account WHERE account.cust_id=customer.cust_id and customer.cust_id = %s', (session['cust_id'],))
                account = cursor.fetchall()
                print(account)
                if(account):
                    return  render_template('custHome.html',accounts=account)
    
    return render_template('index.html',username=user_view, msg='',emp=empVisible,cust=custVisible)


@app.route('/login/<string:emp>', methods=['GET', 'POST'])
def logas(emp):

    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
                return   redirect('/')
            else:
                return  redirect('/')


    if(emp=="employee"):
        global empVisible       
        global custVisible        
  
        global user_view
        custVisible=""
        employee=True
        user_view="Executive-ID"
        empVisible="active"
        return render_template('index.html',username=user_view, msg='',emp=empVisible,cust=custVisible)
    else:
       
        empVisible=""
        custVisible="active"
        employee=False
        user_view="Account/SSN/Customer-ID "
        return render_template('index.html',username=user_view, msg='',emp=empVisible,cust=custVisible)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
                return   redirect('/')
            else:
                return  redirect('/')
  



    msg = ''

    print(request.form)

    if request.method == 'POST' and 'id' in request.form and 'password' in request.form:


        username = request.form['id']
        password = request.form['password']
      
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if(employee):
            cursor.execute('SELECT * FROM empstore WHERE user_id = %s AND password = %s', (username, password))
            # Fetch one record and return result
            account = cursor.fetchone()
            # If account exists 
            if account:
                # Creating session data
                session['loggedin'] = True
                session['userid'] = account['user_id']
                session['employee']= employee

                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                print(timestamp)
                cursor.execute('UPDATE empstore SET timestamp = %s WHERE  user_id = %s;',(timestamp,account['user_id']))
                mysql.connection.commit()
                return  redirect('/')
            else:
                # Account doesnt exist 
                msg = 'Incorrect username/password!!!'
        else:
            try : 
                username= int (username)
                cursor.execute('SELECT  customer.cust_id ,customer.cust_name  FROM customer,account WHERE customer.cust_id=account.cust_id and customer.cust_pass=%s and (customer.cust_id=%s or customer.ssn_id=%s or account.acc_id=%s);', (password,username,username,username))
                account = cursor.fetchone()
                # If account exists 
                if account:
                    session['loggedin'] = True
                    session['cust_id'] = account['cust_id']
                    session['employee']= employee
                # Redirecting to home page
                    return  redirect('/')
                
                else:
                    # Account doesnt exist 
                    
                    msg = 'Incorrect username/password!!!'
            
            except:
                msg = 'Incorrect username/password!!!'
    # Show the login form with message (if any)
    
    return render_template('index.html',username=user_view, msg=msg,emp=empVisible,cust=custVisible)



@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('cust_id', None)
    session.pop('employee', None)
    # Redirect to login page
    return redirect('/')



@app.route('/customers', methods=['GET', 'POST'])
def customers():
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                print(session['userid'])
                cursor.execute('SELECT * FROM customer_status')
                account = cursor.fetchall()
                
                if(account):
                    return render_template('customers.html',customers=account)
                else:
                    return render_template('customers.html', customers=account, msg='No customer details\n Click on Add customer to add customer details')
            

    return redirect('/')


@app.route('/accounts', methods=['GET', 'POST'])
def accounts():
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                print(session['userid'])
                cursor.execute('SELECT account_status.acc_id ,account_status.cust_id ,account_status.status ,account_status.message ,account_status.last_updated,account.acc_type  FROM account_status,account WHERE account_status.acc_id=account.acc_id;')
                account = cursor.fetchall()
                
                if(account):
                    return  render_template('accounts.html',accounts=account)
                else:
                    return render_template('accounts.html', accounts=account, msg='No account details\n Click on Add account to add account details')
            

    return redirect('/')

@app.route('/customers/', methods=['GET', 'POST'])
def searchCustomer():
   
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
                
                if request.method == 'POST' and 'search' in request.form:
                    cid= request.form['search']
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    print(cid)
            
                    cursor.execute('select * from customer_status where ssn_id=%s or cust_id=%s;',(int(cid),int(cid),))
                    account = cursor.fetchall()

                    print('fecting',account)
                
                    if(account):
                        return  render_template('customers.html',customers=account)
            

    return redirect('/customers')


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


@app.route('/customers/details/<int:cid>', methods=['GET', 'POST'])
def customerDetails(cid):
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                print('type',type(cid))
                cursor.execute('SELECT * FROM customer where cust_id= %s ', (int(cid),))
                account = cursor.fetchone()
                
                if(account):
                    print(account)
                    return  render_template('custDetails.html',customer=account)
            

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



@app.route('/customer/createcustomer', methods=['GET', 'POST'])
def createCustomer():

    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
                msg = ''
                if request.method == 'POST' and 'ssn_id' in request.form and 'cust_name' in request.form and 'cust_pass' in request.form and 'age' in request.form and 'add_1' in request.form and 'add_2' in request.form and 'city' in request.form and 'state' in request.form:
                    ssn_id = request.form['ssn_id']
                    cust_name = request.form['cust_name']
                    cust_pass = request.form['cust_pass']
                    age = request.form['age']
                    add_1 = request.form['add_1']
                    add_2 = request.form['add_2']
                    city = request.form['city']
                    state = request.form['state']
                    # Check if customer exists already in database
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    # If account exists show error and validation checks
                    print(ssn_id)
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('SELECT * FROM customer WHERE ssn_id = %s', (ssn_id,))
                    account = cursor.fetchone()
                    # If account exists show error and validation checks
                    if account:
                        msg = 'Customer already exists with the same SSN ID!'
                    elif len(ssn_id)!=9:
                        msg = 'SSN ID should be 9 digits'
                    elif not re.match(r'[A-Za-z]+', cust_name):
                        msg = 'Username must contain only characters'
                    elif not ssn_id or not cust_name or not cust_pass:
                        msg = 'Please fill out the form!'
                    else:
                        # Account doesn't exist and form data is valid, insert into table
                        cursor.execute('INSERT INTO customer(ssn_id, cust_name, cust_pass, age, address_1, address_2, city,state) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)', (ssn_id, cust_name, cust_pass, age, add_1, add_2, city, state))
                        mysql.connection.commit()
                        msg = 'Customer record successfully created'
                        cursor.execute('select cust_id from customer where ssn_id = %s', (ssn_id,))
                        cust_id=(cursor.fetchone())['cust_id']
                        ts = time.time()
                        print("cust id", cust_id)
                        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute('INSERT INTO customer_status(ssn_id ,cust_id ,status ,message ,last_updated) VALUES(%s, %s, %s, %s, %s)', (ssn_id, cust_id, "Active", msg, timestamp))
                        mysql.connection.commit()
                        

                # Show registration form with message (if any)
                return render_template('createcustomer.html', msg=msg)
                
                
            

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

    

@app.route('/customer/updatecustomer/<int:cust_id>', methods=['GET', 'POST'])
def updateCustomer(cust_id):
    
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
                print(request.form)
                if request.method == 'POST' and 'ssn_id' in request.form and 'cust_name' in request.form and 'cust_pass' in request.form and 'age' in request.form and 'add_1' in request.form and 'add_2' in request.form and 'city' in request.form and 'state' in request.form:
                    ssn_id = request.form['ssn_id']
                    cust_name = request.form['cust_name']
                    cust_pass = request.form['cust_pass']
                    age = request.form['age']
                    add_1 = request.form['add_1']
                    add_2 = request.form['add_2']
                    city = request.form['city']
                    state = request.form['state'] 
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    print('type',type(cust_id))
                    cursor.execute('UPDATE customer set cust_name=%s, cust_pass=%s, age=%s, address_1=%s, address_2=%s, city=%s, state=%s WHERE cust_id= %s ', (cust_name, cust_pass, age, add_1, add_2, city, state, int(cust_id)))
                    mysql.connection.commit()

                    ts = time.time()
                    print("cust id", cust_id)
                    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute('UPDATE customer_status set message=%s ,last_updated=%s WHERE cust_id=%s', ("Customer details updated", timestamp, cust_id))
                    mysql.connection.commit()

                    cursor.execute('SELECT * FROM customer WHERE cust_id=%s', (cust_id, ))
                    account = cursor.fetchone()
                    return render_template('custDetails.html',customer=account)
                else:
                    print('form incomplete')
            
          

    return redirect('/')

    


@app.route('/customer/<int:cid>', methods=['GET', 'POST'])
def deleteCustomer(cid):
    if(session):
        if(session["loggedin"]):
            global employee
            employee=session['employee']
            if(employee):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

                cursor.execute('DELETE FROM account_status WHERE cust_id = %s',(cid,))
                mysql.connection.commit()
                msg = 'Account record successfully deleted'
                cursor.execute('DELETE FROM account WHERE cust_id = %s',(cid,))
                mysql.connection.commit()

                cursor.execute('DELETE FROM customer_status WHERE cust_id = %s',(cid,))
                mysql.connection.commit()
                msg = 'Customer record successfully deleted'
                cursor.execute('DELETE FROM customer WHERE cust_id = %s',(cid,))
                mysql.connection.commit()
                
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                print(session['userid'])
                cursor.execute('SELECT * FROM customer_status')
                account = cursor.fetchall()
                
                if(account):
                    return render_template('customers.html', customers=account, msg=msg)
            
          
    
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


