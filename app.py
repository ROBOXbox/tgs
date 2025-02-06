from flask import Flask, render_template_string, url_for, abort
from flask_sqlalchemy import SQLAlchemy
import qrcode
import io
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instruments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model untuk alat musik
class Instrument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f"<Instrument {self.name}>"

# Template untuk halaman utama (seperti halaman indeks Wikipedia)
index_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Wiki Alat Musik</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f9f9f9; }
        .header { background: #336699; color: white; padding: 20px; text-align: center; }
        .container { width: 90%; margin: 20px auto; }
        .card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 20px;
            padding: 15px;
            overflow: hidden;
        }
        .card img { float: left; margin-right: 15px; width: 150px; height: 150px; object-fit: cover; }
        .card h2 { margin-top: 0; }
        .clear { clear: both; }
        .qr { margin-top: 10px; }
        a { color: #336699; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Wiki Alat Musik</h1>
        <p>Kumpulan informasi tentang alat-alat musik</p>
    </div>
    <div class="container">
        {% for instrument in instruments %}
        <div class="card">
            <img src="{{ instrument.image_url }}" alt="{{ instrument.name }}">
            <h2><a href="{{ url_for('instrument_detail', instrument_id=instrument.id) }}">{{ instrument.name }}</a></h2>
            <p>{{ instrument.description[:200] }}{% if instrument.description|length > 200 %}...{% endif %}</p>
            <div class="qr">
                <img src="data:image/png;base64,{{ instrument.qr_code }}" alt="QR Code untuk {{ instrument.name }}">
            </div>
            <div class="clear"></div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# Template untuk halaman detail alat musik (mirip halaman artikel Wikipedia)
detail_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ instrument.name }} - Wiki Alat Musik</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f9f9f9; }
        .header { background: #336699; color: white; padding: 20px; text-align: center; }
        .container { width: 80%; margin: 20px auto; background: white; padding: 20px; border: 1px solid #ddd; border-radius: 4px; }
        .instrument-image { float: right; margin: 0 0 20px 20px; width: 300px; height: 300px; object-fit: cover; }
        .qr { margin-top: 10px; }
        a { color: #336699; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ instrument.name }}</h1>
    </div>
    <div class="container">
        <img class="instrument-image" src="{{ instrument.image_url }}" alt="{{ instrument.name }}">
        <p>{{ instrument.description }}</p>
        <h3>QR Code</h3>
        <p>Scan QR code berikut untuk mendapatkan tautan halaman ini:</p>
        <div class="qr">
            <img src="data:image/png;base64,{{ qr_code }}" alt="QR Code untuk {{ instrument.name }}">
        </div>
        <p><a href="{{ url_for('index') }}">&larr; Kembali ke halaman utama</a></p>
    </div>
</body>
</html>
"""

def generate_qr_code(url):
    """Fungsi untuk membuat QR code dari URL dan mengembalikannya dalam format base64."""
    qr = qrcode.make(url)
    buffered = io.BytesIO()
    qr.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Route untuk halaman utama (indeks)
@app.route("/")
def index():
    instruments = Instrument.query.all()
    instrument_data = []
    for instr in instruments:
        # QR code untuk halaman detail alat musik
        link = url_for("instrument_detail", instrument_id=instr.id, _external=True)
        qr_base64 = generate_qr_code(link)
        instrument_data.append({
            "id": instr.id,
            "name": instr.name,
            "description": instr.description,
            "image_url": instr.image_url,
            "qr_code": qr_base64
        })
    return render_template_string(index_template, instruments=instrument_data)

# Route untuk halaman detail alat musik
@app.route("/instrument/<int:instrument_id>")
def instrument_detail(instrument_id):
    instrument = Instrument.query.get(instrument_id)
    if not instrument:
        abort(404)
    # QR code untuk halaman detail saat ini (agar bisa dibagikan)
    link = url_for("instrument_detail", instrument_id=instrument.id, _external=True)
    qr_base64 = generate_qr_code(link)
    return render_template_string(detail_template, instrument=instrument, qr_code=qr_base64)

# Inisialisasi database dan tambah data contoh
with app.app_context():
    db.create_all()
    if Instrument.query.count() == 0:
        # Data contoh
        data_instruments = [
            {
                "name": "Angklung",
                "description": "Angklung adalah alat musik tradisional Indonesia yang terbuat dari tabung-tabung bambu yang disusun sedemikian rupa sehingga menghasilkan bunyi harmonis ketika digoyangkan.",
                "image_url": "https://via.placeholder.com/300?text=Angklung"
            },
            {
                "name": "Seruling",
                "description": "Seruling adalah alat musik tiup yang biasanya terbuat dari bambu atau logam. Alat musik ini memiliki suara lembut dan sering digunakan dalam berbagai genre musik tradisional maupun modern.",
                "image_url": "https://via.placeholder.com/300?text=Seruling"
            },
            {
                "name": "Gamelan",
                "description": "Gamelan merupakan ansambel musik tradisional yang berasal dari Indonesia. Biasanya terdiri dari berbagai instrumen seperti gong, kendang, dan instrumen logam lainnya.",
                "image_url": "https://via.placeholder.com/300?text=Gamelan"
            }
        ]
        for item in data_instruments:
            instr = Instrument(name=item["name"],
                               description=item["description"],
                               image_url=item["image_url"])
            db.session.add(instr)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)
