from flask import render_template, request, redirect, url_for, flash, session
from .models import *
import smtplib
from email.message import EmailMessage
from werkzeug.utils import secure_filename
import pandas as pd
import plotly.express as px

secret_key = 'supersecretkey'
finale_data = pd.read_csv('static/final_watches.csv')

Rolex_data = finale_data[finale_data['brand'] == 'Rolex']
Rolex_data = Rolex_data.groupby('yop')['price'].mean()

Cartier_data = finale_data[finale_data['brand'] == 'Cartier']
Cartier_data = Cartier_data.groupby('yop')['price'].mean()

AP_data = finale_data[finale_data['brand'] == 'Audemars Piguet']
AP_data = AP_data.groupby('yop')['price'].mean()

Patek_data = finale_data[finale_data['brand'] == 'Patek Philippe']
Patek_data = Patek_data.groupby('yop')['price'].mean()

def init_routes(app):
    
    # Routes
    @app.route('/', methods=['GET', 'POST'])
    def index():
        return render_template('login.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if 'username' in session:
            return redirect(url_for('user'))
    
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            _user = User.query.filter_by(username=username, password=password).first()
            
            if _user:
                session['username'] = username
                return redirect(url_for('user'))
            else:
                flash('Invalid username or password', 'error')
                return redirect(url_for('login'))

        return render_template('login.html')

    @app.route('/adminlogin', methods=['GET', 'POST'])
    def adminlogin():
        if 'username' in session:
            return redirect(url_for('admin'))
    
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            secretkey = request.form['secretkey']
            
            if username == 'admin' and password == 'adminpass' and secretkey == secret_key:
                session['username'] = username
                return redirect(url_for('admin'))
            else:
                flash('Invalid username or password', 'error')
                return redirect(url_for('adminlogin'))

        return render_template('adminlogin.html')
    
    @app.route('/user', methods=['GET', 'POST'])
    def user():
        if 'username' not in session:
            return redirect(url_for('login'))
        products = Product.query.all()
        return render_template('user.html', products=products)
    
    @app.route('/admin', methods=['GET', 'POST'])
    def admin():
        if 'username' not in session:
            return redirect(url_for('login'))
        products = Product.query.all()
        username = session.get('username')
        return render_template('admin.html', products=products, username=username)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            new_username = request.form['newusername']
            new_password = request.form['newpassword']
            confirm_password = request.form['confirmpassword']  # Added line
            email = request.form['email']
            phone = request.form['phone']
            address = request.form['address']
        
            if len(new_password) < 8:  # Added line
                flash('Password must be at least 8 characters long.', 'error')  # Added line
                return redirect(url_for('register'))  # Added line
        
            if new_password != confirm_password:  # Added line
                flash('Passwords do not match. Please try again.', 'error')
                return redirect(url_for('register'))
        
            existing_user = User.query.filter_by(username=new_username).first()
        
            if existing_user:
                flash('Username already exists. Please choose a different username.', 'error')
                return redirect(url_for('register'))
        
            new_user = User(username=new_username, 
                            password=new_password, 
                            email=email,
                            phone=phone, 
                            address=address)
                            
            db.session.add(new_user)
            db.session.commit()
        
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))
    
        return render_template('register.html')

    @app.route('/logout', methods=['GET', 'POST'])
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.route('/email', methods=['POST'])
    def email():
        if request.method == 'POST':
            # Retrieve form data
            name = request.form['name']
            sender_email = request.form['email']
            sender_email_password = request.form['password']
            message_content = request.form['message']
    
            # Construct the email message
            msg = EmailMessage()
            msg['Subject'] = 'Message from {}'.format(name)
            msg['From'] = sender_email  # Replace with your email address
            msg['To'] = 'rida.nasser@outlook.com'
            msg.set_content(message_content)
    
            # Connect to the SMTP server and send the email
            smtp_servers = [
                ('smtp.gmail.com', 587),  # Gmail SMTP server and port
                ('smtp-mail.outlook.com', 587),  # Outlook.com SMTP server and port
                ('smtp.mail.yahoo.com', 587)  # Yahoo Mail SMTP server and port
            ]
    
            for server, port in smtp_servers:
                try:
                    with smtplib.SMTP(server, port) as smtp:
                        smtp.starttls()
                        smtp.login(sender_email, sender_email_password)
                        smtp.send_message(msg)
                        return redirect(url_for('user'))  # Redirect to user page
                    break  # Exit loop if email sent successfully
                except Exception as e:
                    print(f"Failed to send email using {server}:{port}")
                    print(e)
    
            flash('Email sent successfully.', 'success')
            return redirect(url_for('user'))
        else:
            return 'Method not allowed'

    @app.route('/dashboard', methods=['GET', 'POST'])
    def dashboard():

        # Create Plotly line plots for Rolex, Cartier, Audemars Piguet, and Patek Philippe
        fig1 = px.line(x=Rolex_data.index, y=Rolex_data.values, title='Rolex Price Trend')
        fig2 = px.line(x=Cartier_data.index, y=Cartier_data.values, title='Cartier Price Trend')
        fig3 = px.line(x=AP_data.index, y=AP_data.values, title='Audemars Piguet Price Trend')
        fig4 = px.line(x=Patek_data.index, y=Patek_data.values, title='Patek Philippe Price Trend')

        # Convert Plotly figures to HTML
        plot_div1 = fig1.to_html(full_html=False, include_plotlyjs='cdn')
        plot_div2 = fig2.to_html(full_html=False, include_plotlyjs='cdn')
        plot_div3 = fig3.to_html(full_html=False, include_plotlyjs='cdn')
        plot_div4 = fig4.to_html(full_html=False, include_plotlyjs='cdn')

        # Render the template with Plotly plots
        return render_template('admindashboard.html', plot_div1=plot_div1, plot_div2=plot_div2, plot_div3=plot_div3, plot_div4=plot_div4)

    @app.route('/add_product', methods=['GET', 'POST'])
    def add_product():
        if request.method == 'POST':
            image = request.files['image']
            image_filename = secure_filename(image.filename)
            image_data = image.read()

            product_name = request.form['product_name']
            description = request.form['description']
            price = float(request.form['price'])

            new_product = Product(image=image_data, 
                                  image_filename=image_filename, 
                                  product_name=product_name, 
                                  description=description, 
                                  price=price)
            
            db.session.add(new_product)
            db.session.commit()

            return redirect(url_for('admin'))

        return render_template('add_product.html')
    
    @app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
    def edit_product(product_id):
        product = Product.query.get_or_404(product_id)
        if request.method == 'POST':
            image = request.files['image']
            if image:
                image_filename = secure_filename(image.filename)
                image_data = image.read()
                product.image = image_data
                product.image_filename = image_filename
            product.product_name = request.form['product_name']
            product.description = request.form['description']
            product.price = float(request.form['price'])
            db.session.commit()
            return redirect(url_for('admin'))
        return render_template('edit_product.html', product=product)
    
    @app.route('/delete_product/<int:product_id>', methods=['POST'])
    def delete_product(product_id):
        product = Product.query.get_or_404(product_id)
        
        db.session.delete(product)
        db.session.commit()
        
        return redirect(url_for('admin'))
    
    @app.route('/add_to_cart/<int:product_id>', methods=['POST'])
    def add_to_cart(product_id):
        # Check if the request method is POST
        if request.method == 'POST':
            # Retrieve the current user from the session or wherever it's stored
            username= session.get('username')
            # Check if the user is logged in
            if not username:
                flash('Please log in to add products to your cart', 'error')
                return redirect(url_for('login'))

            # Query the user from the database
            user = User.query.filter_by(username=username).first()
            # Check if the user exists
            if not user:
                flash('User not found', 'error')
                return redirect(url_for('user'))

            # Query the product from the database
            product = Product.query.filter_by(product_id=product_id).first()
            # Check if the product exists
            if not product:
                flash('Product not found', 'error')
                return redirect(url_for('user'))
                
            # Check if the user has a cart
            if not user.cart:
                # Create a new cart for the user
                cart = Cart()
                db.session.add(cart)
                user.cart = cart
                db.session.commit()
                flash('Cart created for the user', 'success')

            # Retrieve the user's cart (in case it was just created)
            cart = user.cart
            card=cart.id

            # Check if the product is already in the user's cart
            if product in cart.products:
                flash('Product already in cart', 'error')
                url = url_for('view_cart', cart_id=card)
                # Now you can use the generated URL for redirection or other purposes
                return redirect(url_for('view_cart',cart_id=cart.id))

            # Add the product to the user's cart
            cart.products.append(product)
            db.session.commit()

            flash('Product added to cart successfully', 'success')
            # Redirect to the view cart page
            return redirect(url_for('view_cart',cart_id=card))
        else:
            flash('Method not allowed', 'error')
            return redirect(url_for('user'))

    @app.route('/view_cart/')
    def view_cart():
        cart_id = request.args.get('cart_id')
        
        # Initialize cart_contents and total_price variables
        cart_contents = []
        total_price = 0.0
        if cart_id is not None:
            cart = Cart.query.get(cart_id)
            if cart:
                # Retrieve the products associated with the cart
                cart_contents = cart.products

                # Calculate the total price of all products in the cart
                total_price = sum(product.price for product in cart_contents)

            else:
                flash('Cart not found', 'error')
        else:
            flash('Cart ID not provided', 'error')

        # Render the template with cart contents and total price
        return render_template('view_cart.html', cart_contents=cart_contents, total_price=total_price)

    @app.route('/users')
    def view_users():
        users = User.query.all()
        return render_template('view_users.html', users=users)

    @app.route('/delete_user/<int:user_id>', methods=['POST'])
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)
        
        db.session.delete(user)
        db.session.commit()
        
        return redirect(url_for('admin'))
    
    # clears cache after signing out so the user cannot go back in without logging in again
    @app.after_request
    def add_header(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
