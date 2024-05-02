from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(50), unique=True, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    cart = db.relationship('Cart', back_populates='user', uselist=False)

    def __init__(self, username, password, email, phone, address):
        self.username = username
        self.password = password
        self.email = email
        self.phone = phone
        self.address = address

class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary)
    image_filename = db.Column(db.String(100))
    product_name = db.Column(db.String(100))
    description = db.Column(db.String(200))
    price = db.Column(db.Float)

    def __init__(self, image, image_filename, product_name, price, description):
        self.image = image
        self.image_filename = image_filename
        self.product_name = product_name
        self.price = price
        self.description = description

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), unique=True)
    user = db.relationship('User', back_populates='cart')
    products = db.relationship('Product', secondary='cart_product_association', backref='carts')

class CartProductAssociation(db.Model):
    __tablename__ = 'cart_product_association'
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), primary_key=True)
