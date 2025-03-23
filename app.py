from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Mock database
users = {
    'user1@example.com': {'password': 'password123', 'name': 'John Doe', 'is_vendor': False, 'is_admin': False},
    'vendor1@example.com': {'password': 'vendor123', 'name': 'Vendor Store', 'is_vendor': True, 'is_admin': False},
    'admin@example.com': {'password': 'admin123', 'name': 'Admin User', 'is_vendor': False, 'is_admin': True}
}

products = [
    {
        'id': '1',
        'name': 'Cryptocurrency Hardware Wallet',
        'price': 79.99,
        'description': 'Secure hardware wallet for storing your cryptocurrencies offline.',
        'vendor': 'Vendor Store',
        'category': 'Hardware',
        'image': 'https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=400',
        'status': 'approved',
        'created_at': '2025-03-15 10:30:00'
    },
    {
        'id': '2',
        'name': 'Blockchain for Beginners Book',
        'price': 29.99,
        'description': 'Comprehensive introduction to blockchain technology and cryptocurrencies.',
        'vendor': 'Vendor Store',
        'category': 'Books',
        'image': 'https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=400',
        'status': 'approved',
        'created_at': '2025-03-16 14:20:00'
    },
    {
        'id': '3',
        'name': 'Mining Rig Cooling System',
        'price': 149.99,
        'description': 'High-performance cooling system for cryptocurrency mining rigs.',
        'vendor': 'Vendor Store',
        'category': 'Hardware',
        'image': 'https://images.unsplash.com/photo-1518932945647-7a1c969f8be2?w=400',
        'status': 'pending',
        'created_at': '2025-03-22 09:45:00'
    }
]

orders = []

# Mock escrow data
escrows = []

# Function to generate a mock escrow address
def generate_escrow_address():
    return f"bc1q{uuid.uuid4().hex[:32]}"

# Website statistics for admin dashboard
site_stats = {
    'total_users': 3,
    'total_vendors': 1,
    'total_products': 3,
    'total_orders': 0,
    'total_revenue': 0,
    'pending_products': 1
}

# Activity logs for admin monitoring
activity_logs = [
    {'user': 'vendor1@example.com', 'action': 'Added new product: Mining Rig Cooling System', 'timestamp': '2025-03-22 09:45:00'},
    {'user': 'vendor1@example.com', 'action': 'Added new product: Blockchain for Beginners Book', 'timestamp': '2025-03-16 14:20:00'},
    {'user': 'vendor1@example.com', 'action': 'Added new product: Cryptocurrency Hardware Wallet', 'timestamp': '2025-03-15 10:30:00'},
    {'user': 'admin@example.com', 'action': 'Approved product: Blockchain for Beginners Book', 'timestamp': '2025-03-16 15:05:00'},
    {'user': 'admin@example.com', 'action': 'Approved product: Cryptocurrency Hardware Wallet', 'timestamp': '2025-03-15 11:10:00'}
]

@app.route('/')
def home():
    approved_products = [p for p in products if p['status'] == 'approved']
    return render_template('index.html', products=approved_products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email in users and users[email]['password'] == password:
            session['logged_in'] = True
            session['email'] = email
            session['name'] = users[email]['name']
            session['is_vendor'] = users[email]['is_vendor']
            session['is_admin'] = users[email]['is_admin']
            flash('You were successfully logged in')
            return redirect(url_for('home'))
        else:
            error = 'Invalid credentials. Please try again.'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('email', None)
    session.pop('name', None)
    session.pop('is_vendor', None)
    session.pop('is_admin', None)
    flash('You were successfully logged out')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        is_vendor = 'is_vendor' in request.form

        if email in users:
            error = 'Email already registered. Please use a different email.'
        else:
            users[email] = {
                'password': password,
                'name': name,
                'is_vendor': is_vendor,
                'is_admin': False
            }

            # Update site statistics
            site_stats['total_users'] += 1
            if is_vendor:
                site_stats['total_vendors'] += 1

            # Log the activity
            activity_logs.append({
                'user': email,
                'action': f'User registration: {name}' + (' (Vendor)' if is_vendor else ''),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))

    return render_template('register.html', error=error)

@app.route('/product/<product_id>')
def product_detail(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product and (product['status'] == 'approved' or (session.get('is_admin') or (session.get('is_vendor') and product['vendor'] == session.get('name')))):
        return render_template('product_detail.html', product=product)
    return redirect(url_for('home'))

# ... existing cart routes ...
@app.route('/cart')
def view_cart():
    if 'cart' not in session:
        session['cart'] = []

    cart_items = []
    total = 0

    for item in session['cart']:
        product = next((p for p in products if p['id'] == item['product_id']), None)
        if product:
            cart_item = {
                'product_id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': item['quantity'],
                'subtotal': product['price'] * item['quantity']
            }
            cart_items.append(cart_item)
            total += cart_item['subtotal']

    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])

    if 'cart' not in session:
        session['cart'] = []

    # Check if product already in cart, update quantity if so
    cart = session['cart']
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            session['cart'] = cart
            flash('Cart updated successfully')
            return redirect(url_for('view_cart'))

    # Add new item to cart
    cart.append({'product_id': product_id, 'quantity': quantity})
    session['cart'] = cart
    flash('Item added to cart')
    return redirect(url_for('view_cart'))

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = request.form['product_id']

    if 'cart' in session:
        cart = session['cart']
        cart = [item for item in cart if item['product_id'] != product_id]
        session['cart'] = cart
        flash('Item removed from cart')

    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty')
        return redirect(url_for('view_cart'))

    if not session.get('logged_in'):
        flash('Please log in to proceed with checkout')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Process the order
        order_id = str(uuid.uuid4())
        order_total = sum(p['price'] * item['quantity']
                         for item in session['cart']
                         for p in products if p['id'] == item['product_id'])

        order = {
            'id': order_id,
            'user_email': session['email'],
            'items': session['cart'],
            'total': order_total,
            'shipping_address': request.form['shipping_address'],
            'payment_address': request.form['payment_address'],
            'status': 'Pending',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'escrow_status': 'awaiting_payment'
        }
        orders.append(order)

        # Generate an escrow for the order
        escrow_address = generate_escrow_address()
        escrow = {
            'id': str(uuid.uuid4()),
            'order_id': order_id,
            'escrow_address': escrow_address,
            'amount': order_total,
            'status': 'awaiting_payment',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'funded_at': None,
            'released_at': None,
            'dispute_reason': None,
            'dispute_resolved_at': None,
            'admin_notes': None
        }
        escrows.append(escrow)

        # Update site statistics
        site_stats['total_orders'] += 1
        site_stats['total_revenue'] += order_total

        # Log the activity
        activity_logs.append({
            'user': session['email'],
            'action': f'New order placed: ${order_total:.2f}',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

        # Clear the cart
        session['cart'] = []

        flash('Order placed successfully')
        return redirect(url_for('order_confirmation', order_id=order_id))

    cart_items = []
    total = 0

    for item in session['cart']:
        product = next((p for p in products if p['id'] == item['product_id']), None)
        if product:
            cart_item = {
                'product_id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': item['quantity'],
                'subtotal': product['price'] * item['quantity']
            }
            cart_items.append(cart_item)
            total += cart_item['subtotal']

    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/order_confirmation/<order_id>')
def order_confirmation(order_id):
    order = next((o for o in orders if o['id'] == order_id), None)
    escrow = next((e for e in escrows if e['order_id'] == order_id), None)

    if order:
        order_items = []
        for item in order['items']:
            product = next((p for p in products if p['id'] == item['product_id']), None)
            if product:
                order_items.append({
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': item['quantity'],
                    'subtotal': product['price'] * item['quantity']
                })

        return render_template('order_confirmation.html', order=order, order_items=order_items, escrow=escrow)

    flash('Order not found')
    return redirect(url_for('home'))

# ... existing code ... <up to the dashboard route>

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        flash('Please log in to access the dashboard')
        return redirect(url_for('login'))

    if not session.get('is_vendor'):
        # For regular users (buyers), show their orders
        user_orders = [o for o in orders if o['user_email'] == session['email']]
        user_escrows = []

        for order in user_orders:
            order_escrow = next((e for e in escrows if e['order_id'] == order['id']), None)
            if order_escrow:
                user_escrows.append(order_escrow)

        return render_template('buyer_dashboard.html', orders=user_orders, escrows=user_escrows)
    else:
        # For vendors, show orders for their products
        vendor_orders = [o for o in orders if any(
            p['vendor'] == session['name']
            for item in o['items']
            for p in products if p['id'] == item['product_id']
        )]

        vendor_products = [p for p in products if p['vendor'] == session['name']]

        # Get escrows for vendor orders
        vendor_escrows = []
        for order in vendor_orders:
            order_escrow = next((e for e in escrows if e['order_id'] == order['id']), None)
            if order_escrow:
                vendor_escrows.append(order_escrow)

        return render_template('dashboard.html', orders=vendor_orders, products=vendor_products, escrows=vendor_escrows)

# ... existing code ... <add_product route>

# Escrow-related routes
@app.route('/escrow/<escrow_id>')
def escrow_detail(escrow_id):
    if not session.get('logged_in'):
        flash('Please log in to view escrow details')
        return redirect(url_for('login'))

    escrow = next((e for e in escrows if e['id'] == escrow_id), None)
    if not escrow:
        flash('Escrow not found')
        return redirect(url_for('dashboard'))

    order = next((o for o in orders if o['id'] == escrow['order_id']), None)
    if not order:
        flash('Order not found')
        return redirect(url_for('dashboard'))

    # Check if user has permission (buyer, seller or admin)
    is_buyer = order['user_email'] == session['email']
    is_seller = any(p['vendor'] == session['name'] for item in order['items'] for p in products if p['id'] == item['product_id'])

    if not (is_buyer or is_seller or session.get('is_admin')):
        flash('You do not have permission to view this escrow')
        return redirect(url_for('dashboard'))

    # Get order items for display
    order_items = []
    for item in order['items']:
        product = next((p for p in products if p['id'] == item['product_id']), None)
        if product:
            order_items.append({
                'name': product['name'],
                'price': product['price'],
                'quantity': item['quantity'],
                'subtotal': product['price'] * item['quantity'],
                'vendor': product['vendor']
            })

    return render_template('escrow_detail.html', escrow=escrow, order=order, order_items=order_items,
                           is_buyer=is_buyer, is_seller=is_seller)

@app.route('/escrow/<escrow_id>/simulate_payment', methods=['POST'])
def simulate_payment(escrow_id):
    if not session.get('logged_in'):
        flash('Please log in to perform this action')
        return redirect(url_for('login'))

    escrow = next((e for e in escrows if e['id'] == escrow_id), None)
    if not escrow:
        flash('Escrow not found')
        return redirect(url_for('dashboard'))

    order = next((o for o in orders if o['id'] == escrow['order_id']), None)
    if not order:
        flash('Order not found')
        return redirect(url_for('dashboard'))

    # Only the buyer can simulate payment
    if order['user_email'] != session['email'] and not session.get('is_admin'):
        flash('You do not have permission to perform this action')
        return redirect(url_for('dashboard'))

    # Update escrow status
    escrow['status'] = 'in_escrow'
    escrow['funded_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    escrow['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Update order escrow status
    order['escrow_status'] = 'in_escrow'

    # Log the activity
    activity_logs.append({
        'user': session['email'],
        'action': f'Payment received for order #{order["id"][:8]} (${escrow["amount"]:.2f})',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    flash('Payment simulation successful. Funds are now in escrow.')
    return redirect(url_for('escrow_detail', escrow_id=escrow_id))

@app.route('/escrow/<escrow_id>/release', methods=['POST'])
def release_escrow(escrow_id):
    if not session.get('logged_in'):
        flash('Please log in to perform this action')
        return redirect(url_for('login'))

    escrow = next((e for e in escrows if e['id'] == escrow_id), None)
    if not escrow:
        flash('Escrow not found')
        return redirect(url_for('dashboard'))

    order = next((o for o in orders if o['id'] == escrow['order_id']), None)
    if not order:
        flash('Order not found')
        return redirect(url_for('dashboard'))

    # Only the buyer or admin can release escrow
    if order['user_email'] != session['email'] and not session.get('is_admin'):
        flash('You do not have permission to release funds')
        return redirect(url_for('dashboard'))

    # Ensure escrow is in the correct state
    if escrow['status'] != 'in_escrow':
        flash('Cannot release funds at this time. Funds must be in escrow to be released.')
        return redirect(url_for('escrow_detail', escrow_id=escrow_id))

    # Update escrow status
    escrow['status'] = 'released'
    escrow['released_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    escrow['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Update order status
    order['escrow_status'] = 'released'
    order['status'] = 'Completed'

    # Log the activity
    activity_logs.append({
        'user': session['email'],
        'action': f'Funds released for order #{order["id"][:8]} (${escrow["amount"]:.2f})',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    flash('Funds have been released to the seller.')
    return redirect(url_for('escrow_detail', escrow_id=escrow_id))

@app.route('/escrow/<escrow_id>/dispute', methods=['GET', 'POST'])
def dispute_escrow(escrow_id):
    if not session.get('logged_in'):
        flash('Please log in to perform this action')
        return redirect(url_for('login'))

    escrow = next((e for e in escrows if e['id'] == escrow_id), None)
    if not escrow:
        flash('Escrow not found')
        return redirect(url_for('dashboard'))

    order = next((o for o in orders if o['id'] == escrow['order_id']), None)
    if not order:
        flash('Order not found')
        return redirect(url_for('dashboard'))

    # Only the buyer can initiate a dispute
    if order['user_email'] != session['email']:
        flash('You do not have permission to initiate a dispute')
        return redirect(url_for('dashboard'))

    # Ensure escrow is in the correct state
    if escrow['status'] != 'in_escrow':
        flash('Cannot dispute at this time. Funds must be in escrow to initiate a dispute.')
        return redirect(url_for('escrow_detail', escrow_id=escrow_id))

    if request.method == 'POST':
        dispute_reason = request.form.get('dispute_reason', '')
        if not dispute_reason:
            flash('Please provide a reason for the dispute')
            return redirect(url_for('dispute_escrow', escrow_id=escrow_id))

        # Update escrow status
        escrow['status'] = 'disputed'
        escrow['dispute_reason'] = dispute_reason
        escrow['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Update order status
        order['escrow_status'] = 'disputed'

        # Log the activity
        activity_logs.append({
            'user': session['email'],
            'action': f'Dispute opened for order #{order["id"][:8]}: {dispute_reason[:50]}...',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

        flash('Dispute has been submitted and will be reviewed by the marketplace admin.')
        return redirect(url_for('escrow_detail', escrow_id=escrow_id))

    return render_template('dispute_form.html', escrow=escrow, order=order)

@app.route('/admin/escrows')
def admin_escrows():
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('You must be logged in as an admin to access this page')
        return redirect(url_for('login'))

    # Filter escrows by status if specified
    status_filter = request.args.get('status', 'all')

    if status_filter != 'all':
        filtered_escrows = [e for e in escrows if e['status'] == status_filter]
    else:
        filtered_escrows = escrows

    # Add order info to escrows for display
    escrow_details = []
    for escrow in filtered_escrows:
        order = next((o for o in orders if o['id'] == escrow['order_id']), None)
        if order:
            escrow_details.append({
                'escrow': escrow,
                'order': order
            })

    return render_template('admin/escrows.html', escrow_details=escrow_details, current_status=status_filter)

@app.route('/admin/escrow/<escrow_id>', methods=['GET', 'POST'])
def admin_escrow_detail(escrow_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('You must be logged in as an admin to access this page')
        return redirect(url_for('login'))

    escrow = next((e for e in escrows if e['id'] == escrow_id), None)
    if not escrow:
        flash('Escrow not found')
        return redirect(url_for('admin_escrows'))

    order = next((o for o in orders if o['id'] == escrow['order_id']), None)
    if not order:
        flash('Order not found')
        return redirect(url_for('admin_escrows'))

    if request.method == 'POST':
        action = request.form.get('action')
        admin_notes = request.form.get('admin_notes', '')

        if action == 'refund':
            # Process refund to buyer
            escrow['status'] = 'refunded'
            escrow['admin_notes'] = admin_notes
            escrow['dispute_resolved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            escrow['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            order['escrow_status'] = 'refunded'
            order['status'] = 'Cancelled'

            # Log the activity
            activity_logs.append({
                'user': session['email'],
                'action': f'Admin refunded escrow for order #{order["id"][:8]} (${escrow["amount"]:.2f})',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            flash('Funds have been refunded to the buyer.')

        elif action == 'release':
            # Release funds to seller
            escrow['status'] = 'released'
            escrow['admin_notes'] = admin_notes
            escrow['released_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            escrow['dispute_resolved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if escrow['status'] == 'disputed' else None
            escrow['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            order['escrow_status'] = 'released'
            order['status'] = 'Completed'

            # Log the activity
            activity_logs.append({
                'user': session['email'],
                'action': f'Admin released escrow for order #{order["id"][:8]} (${escrow["amount"]:.2f})',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            flash('Funds have been released to the seller.')

        return redirect(url_for('admin_escrow_detail', escrow_id=escrow_id))

    # Get order items for display
    order_items = []
    for item in order['items']:
        product = next((p for p in products if p['id'] == item['product_id']), None)
        if product:
            order_items.append({
                'name': product['name'],
                'price': product['price'],
                'quantity': item['quantity'],
                'subtotal': product['price'] * item['quantity'],
                'vendor': product['vendor']
            })

    return render_template('admin/escrow_detail.html', escrow=escrow, order=order, order_items=order_items)

@app.route('/admin/order/<order_id>')
def admin_order_detail(order_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('You must be logged in as an admin to access this page')
        return redirect(url_for('login'))

    order = next((o for o in orders if o['id'] == order_id), None)
    if not order:
        flash('Order not found')
        return redirect(url_for('admin_orders'))

    # Get escrow information for this order
    escrow = next((e for e in escrows if e['order_id'] == order_id), None)

    order_items = []
    for item in order['items']:
        product = next((p for p in products if p['id'] == item['product_id']), None)
        if product:
            order_items.append({
                'name': product['name'],
                'price': product['price'],
                'quantity': item['quantity'],
                'subtotal': product['price'] * item['quantity'],
                'vendor': product['vendor']
            })

    return render_template('admin/order_detail.html', order=order, order_items=order_items, escrow=escrow)

# ... existing code ... <rest of the routes>

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
