import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///supply_chain_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration for Image Uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Database Model ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False)
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')

    @property
    def status_label(self):
        if self.quantity == 0: return "Out of Stock"
        elif self.quantity < 10: return "Limited Stock"
        else: return "In Stock"

    @property
    def status_color(self):
        if self.quantity == 0: return "danger"
        elif self.quantity < 10: return "warning"
        return "success"

with app.app_context():
    db.create_all()

# --- Routes ---

@app.route('/', methods=['GET'])
def index():
    query = request.args.get('q', '').strip()
    products = []

    if query:
        q_lower = query.lower()
        if q_lower in ['out of stock', 'empty', 'none']:
            products = Product.query.filter(Product.quantity == 0).all()
        elif q_lower in ['limited', 'low']:
            products = Product.query.filter(Product.quantity > 0, Product.quantity < 10).all()
        elif q_lower in ['available', 'in stock']:
             products = Product.query.filter(Product.quantity >= 10).all()
        else:
            search = f"%{query}%"
            products = Product.query.filter(
                or_(
                    Product.product_name.ilike(search),
                    Product.description.ilike(search),
                    Product.vendor_name.ilike(search)
                )
            ).all()
    else:
        products = Product.query.order_by(Product.id.desc()).all()

    return render_template('index.html', products=products, query=query)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        vendor = request.form.get('vendor_name')
        p_name = request.form.get('product_name')
        desc = request.form.get('description')
        
        try:
            qty = int(request.form.get('quantity'))
            price = float(request.form.get('price'))
        except ValueError:
            flash('Invalid numbers provided', 'danger')
            return redirect(url_for('upload'))

        # Handle Image Upload
        file = request.files.get('product_image')
        filename = 'default.jpg' 
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_product = Product(
            vendor_name=vendor,
            product_name=p_name,
            description=desc,
            quantity=qty,
            price=price,
            image_file=filename
        )

        try:
            db.session.add(new_product)
            db.session.commit()
            flash('Product uploaded successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')

    return render_template('upload.html')

# --- NEW EDIT ROUTE ---
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.vendor_name = request.form.get('vendor_name')
        product.product_name = request.form.get('product_name')
        product.description = request.form.get('description')
        
        try:
            product.quantity = int(request.form.get('quantity'))
            product.price = float(request.form.get('price'))
        except ValueError:
            flash('Invalid numbers provided', 'danger')
            return redirect(url_for('edit_product', id=id))

        # Check if a new image is uploaded
        file = request.files.get('product_image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.image_file = filename # Update filename only if new image exists

        try:
            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error updating product: {e}', 'danger')

    return render_template('edit.html', product=product)

# --- NEW DELETE ROUTE (Optional but helpful) ---
@app.route('/delete/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted.', 'info')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error deleting: {e}', 'danger')
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)