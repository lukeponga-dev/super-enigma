from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

# Association table for order items (many-to-many relationship)
order_items = db.Table('order_items',
    db.Column('order_id', db.String(36), db.ForeignKey('orders.id'), primary_key=True),
    db.Column('product_id', db.String(36), db.ForeignKey('products.id'), primary_key=True),
    db.Column('quantity', db.Integer, nullable=False, default=1),
    db.Column('price_at_time', db.Float, nullable=False)  # Price when ordered (snapshot)
)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_vendor = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    products = db.relationship('Product', backref='vendor_user', lazy='dynamic')
    orders = db.relationship('Order', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email}>'

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    vendor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    payment_address = db.Column(db.String(255), nullable=False)  # Crypto wallet address
    status = db.Column(db.String(20), default='Pending')  # Pending, Shipped, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    escrow_status = db.Column(db.String(30), default='awaiting_payment')  # New field for escrow status

    # Relationship for order items
    products = db.relationship('Product', secondary=order_items, backref='orders')

    # Relationship for escrow
    escrow = db.relationship('Escrow', backref='order', uselist=False)

    def __repr__(self):
        return f'<Order {self.id}>'

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 can be up to 45 chars
    user_agent = db.Column(db.String(255), nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON or additional context

    # Relationship
    user = db.relationship('User', backref='activity_logs')

    def __repr__(self):
        return f'<ActivityLog {self.id}>'

# For storing crypto transaction details
class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    crypto_currency = db.Column(db.String(20), nullable=False)  # BTC, ETH, etc.
    wallet_address = db.Column(db.String(255), nullable=False)
    transaction_hash = db.Column(db.String(255), nullable=True)  # Blockchain TX hash
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)

    # Relationship
    order = db.relationship('Order', backref='transactions')

    def __repr__(self):
        return f'<Transaction {self.id}>'

# New Escrow model
class Escrow(db.Model):
    __tablename__ = 'escrows'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False, unique=True)
    escrow_address = db.Column(db.String(255), nullable=False)  # Generated escrow wallet address
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default='awaiting_payment')
    # Possible statuses: awaiting_payment, payment_received, in_escrow, released, refunded, disputed
    funded_at = db.Column(db.DateTime, nullable=True)
    released_at = db.Column(db.DateTime, nullable=True)
    dispute_reason = db.Column(db.Text, nullable=True)
    dispute_resolved_at = db.Column(db.DateTime, nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Escrow {self.id}>'
