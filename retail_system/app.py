from flask import Flask,redirect,render_template,url_for,request,flash,session
from config import get_connection


app = Flask(__name__)

app.secret_key = 'retail123'


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        u = request.form['username']
        p = request.form['password']
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users(username,password) VALUES(%s,%s)", (u,p))
            conn.commit()
            cur.close()
            conn.close()
            flash("Register successfully")
            return redirect('/')
        except:
            conn.close()
            flash("User exists")
    return render_template('register.html')

@app.route('/', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u = request.form['username']
        p = request.form['password']
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE username=%s", (u,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row and row['password']== p:
            session['user_id'] = row['id']
            session['username'] = u
            return redirect('/home')
        flash("Invalid username or password")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/products')

def products():
    conn = get_connection()
    cur = conn.cursor(dictionary=True) 
    cur.execute("SELECT * FROM products")
    data = cur.fetchall()
    conn.close()
    return render_template('products.html',products=data)

@app.route('/add_product',methods = ['POST','GET'])

def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        stock = request.form.get('stock')

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO products (name,price,stock) VALUES(%s,%s,%s)',(name,price,stock))
        conn.commit()
        cur.close()
        conn.close()

        flash("Product is added successfully",'success')
        return redirect(url_for("products"))
    return render_template("add_product.html")


@app.route('/edit_product/<int:pid>',methods=['GET','POST'])

def edit_product(pid):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        stock = request.form.get('stock')

        cur.execute('UPDATE products SET name=%s,price=%s,stock=%s WHERE product_id=%s',(name,price,stock,pid))
        conn.commit()
        cur.close()
        conn.close()

        flash('Product updated successfully','success')
        return redirect(url_for("products"))
    
    cur.execute('SELECT * FROM products WHERE product_id=%s',(pid,))
    product = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_product.html",product=product)

@app.route('/delete_product/<int:pid>')

def delete_product(pid):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM products WHERE product_id=%s',(pid,))
        conn.commit()
        flash("product deleted successfully.",'success')
    except Exception as e:
        flash('Cannot delete product (maybe referenced by invoices)','danger')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for("products"))


@app.route('/customers')
def customers():
    conn = get_connection()
    cur =conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM customers')
    customers = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("customers.html",customers=customers)

@app.route('/add_customers',methods=['GET','POST'])
def add_customers():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')   
        phone = request.form.get('phone')  
        premier =1 if request.form.get('premier') == 'on' else 0
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO customers (name,email,phone,premier) VALUES(%s,%s,%s,%s)',(name,email,phone,premier))
        conn.commit()
        cur.close()
        conn.close()
        flash ("Customer added successfully",'success')
        return redirect (url_for("customers"))
    return render_template("add_customer.html")

@app.route('/edit_customer/<int:cid>',methods=['GET','POST'])
def edit_customer(cid):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')   
        phone = request.form.get('phone')  
        premier =1 if request.form.get('premier') == 'on' else 0

        cur.execute('UPDATE customers SET name=%s,email=%s,phone=%s,premier=%s WHERE customer_id=%s',(name,email,phone,premier,cid))
        conn.commit()
        cur.close()
        conn.close()
        flash ("customer data updated successfully",'success')
        return redirect(url_for("customers"))
    cur.execute('SELECT * FROM customers WHERE customer_id=%s',(cid,))
    customer = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_customer.html",customer=customer)


@app.route('/delete_customer/<int:cid>')
def delete_customer(cid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM customers WHERE customer_id=%s',(cid,))
    conn.commit()
    cur.close()
    conn.close()
    flash("customer deleted successfully",'success')
    return redirect(url_for('customers'))


#Billig page

@app.route('/billing', methods=['GET', 'POST'])
def billing():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    
    cur.execute('SELECT * FROM products')
    products = cur.fetchall()
    cur.execute('SELECT * FROM customers')
    customers = cur.fetchall()

    
    row_count = int(request.form.get("row_count", 1))
    product_ids = request.form.getlist('product_id[]')
    quantities = request.form.getlist('quantity[]')
    customer_id = request.form.get('customer_id', '')

    if request.method == 'POST':

        
        if 'add_row' in request.form:
            row_count += 1
            cur.close(); conn.close()
            return render_template('billing.html',
                                   products=products,
                                   customers=customers,
                                   row_count=row_count,
                                   customer_id=customer_id,
                                   product_ids=product_ids,
                                   quantities=quantities)

        
        if 'delete_row' in request.form:
            delete_index = int(request.form.get('delete_row'))
            if delete_index < len(product_ids):
                product_ids.pop(delete_index)
                quantities.pop(delete_index)
            row_count = max(len(product_ids), 1)
            cur.close(); conn.close()
            return render_template('billing.html',
                                   products=products,
                                   customers=customers,
                                   row_count=row_count,
                                   customer_id=customer_id,
                                   product_ids=product_ids,
                                   quantities=quantities)

        
        if 'submit_invoice' in request.form:
            total_invoice_amount = 0
            stock_error = False
            error_messages = []
            for pid, qty in zip(product_ids, quantities):
                if not pid or not qty or int(qty) <= 0:
                    continue
                qty = int(qty)

                cur.execute('SELECT name, stock, price FROM products WHERE product_id=%s', (pid,))
                product = cur.fetchone()
                if not product:
                    continue
                name = product['name']
                stock = int(product['stock'])
                price = float(product['price'])
                if qty > stock:
                    stock_error = True
                    error_messages.append(f"⚠️ '{name}' stock is {stock}, cannot bill {qty}.")

            if stock_error:
                flash(' '.join(error_messages), 'error')
                cur.close(); conn.close()
                return render_template('billing.html',
                                       products=products,
                                       customers=customers,
                                       row_count=max(len(product_ids), row_count),
                                       customer_id=customer_id,
                                       product_ids=product_ids,
                                       quantities=quantities)

            cur.execute("INSERT INTO invoices (customer_id, total_amount) VALUES (%s, %s)",
                        (customer_id if customer_id else None, 0))
            invoice_id = cur.lastrowid

            for pid, qty in zip(product_ids, quantities):
                if not pid or not qty or int(qty) <= 0:
                    continue
                qty = int(qty)

                
                cur.execute('SELECT price FROM products WHERE product_id=%s', (pid,))
                product = cur.fetchone()
                price = float(product['price'])
                total_invoice_amount += price * qty             

                
                cur.execute(
                    'INSERT INTO invoice_items (invoice_id, product_id, quantity, price) VALUES (%s,%s,%s,%s)',
                    (invoice_id, pid, qty, price)
                )

                
                cur.execute('UPDATE products SET stock=GREATEST(stock - %s, 0) WHERE product_id=%s',
                            (qty, pid))

            
            if total_invoice_amount > 1000 and customer_id:
                final_amount = total_invoice_amount * 0.9  # 10% discount
                cur.execute('UPDATE customers SET premier=1 WHERE customer_id=%s', (customer_id,))
            else:
                final_amount = total_invoice_amount

            
            cur.execute('UPDATE invoices SET total_amount=%s WHERE invoice_id=%s', (final_amount, invoice_id))

            conn.commit()
            cur.close(); conn.close()

            flash(f'Invoice created successfully. Total: ${final_amount:.2f}', 'success')
            return redirect(url_for('view_invoice', invoice_id=invoice_id))

    
    cur.close(); conn.close()
    return render_template('billing.html',
                           products=products,
                           customers=customers,
                           row_count=max(len(product_ids), row_count),
                           customer_id=customer_id,
                           product_ids=product_ids,
                           quantities=quantities)


@app.route('/invoice/<int:invoice_id>')
def view_invoice(invoice_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    
    cur.execute("""
        SELECT i.invoice_id, i.customer_id, i.total_amount, i.created_at,
               c.name AS customer_name, c.premier
        FROM invoices i
        JOIN customers c ON i.customer_id = c.customer_id
        WHERE i.invoice_id = %s
    """, (invoice_id,))
    invoice = cur.fetchone()

    if not invoice:
        cur.close()
        conn.close()
        flash("Invoice not found", "danger")
        return redirect(url_for('billing'))

    
    cur.execute("""
        SELECT ii.product_id, ii.quantity, ii.price, p.name
        FROM invoice_items ii
        JOIN products p ON ii.product_id = p.product_id
        WHERE ii.invoice_id = %s
    """, (invoice_id,))
    items = cur.fetchall()

    
    subtotal = sum(item['quantity'] * item['price'] for item in items)
    discount = subtotal - invoice['total_amount']

    cur.close()
    conn.close()
    return render_template('view_invoice.html',
                           invoice=invoice,
                           items=items,
                           subtotal=subtotal,
                           discount=discount)


@app.route('/admin')

def admin():
    conn = get_connection()
    cur=conn.cursor(dictionary=True)
    cur.execute('SELECT COUNT(*) AS total FROM products')
    total_p= cur.fetchone()["total"]
    cur.execute('SELECT COUNT(*) AS total FROM customers')
    total_c= cur.fetchone()["total"]
    cur.execute('SELECT COUNT(*) AS total FROM customers WHERE premier = 1')
    premium =cur.fetchone()['total']
    cur.close()
    conn.close()

    return render_template(
        'admin_dashboard.html',
        total_products=total_p,
        total_customers=total_c,
        premium_customers=premium,
    )

@app.route('/invoices')

def invoices():
    conn = get_connection()
    cur=conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM invoices ORDER BY created_at DESC')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('invoices.html',invoices=data)

@app.route('/predict_demand')

def predict_demand():
    conn = get_connection()
    cur=conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM products')
    products=cur.fetchall()

    result = []
    for p in products:
        pid=p['product_id']
        stock=float(p['stock'])

        cur.execute(''' SELECT IFNULL(SUM(quantity),0) AS sold
                    FROM invoice_items
                    WHERE product_id=%s AND created_at >= NOW() - INTERVAL 30 DAY
        ''', (pid,))
        row = cur.fetchone()
        sold_30 = float(row['sold'] if row else 0)

        avg_daily = sold_30 / 30.0
        predicted_7 = round(avg_daily * 7, 2)

        status = 'OK'
        if predicted_7 > stock:
            status = '⚠️ Low Stock Predicted...Restock Soon!'

        result.append({
            'product_id': pid,
            'name': p['name'],
            'stock': stock,
            'sold_30': sold_30,
            'predicted_7': predicted_7,
            'status': status
        })

    cur.close()
    conn.close()
    return render_template('predict.html', results=result)


if __name__=='__main__':
    app.run(debug=True) 