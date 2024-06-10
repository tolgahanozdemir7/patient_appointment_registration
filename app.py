from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hastane_sistemi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Kullanici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_soyad = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    sifre = db.Column(db.String(100))
    il = db.Column(db.String(50))
    ilce = db.Column(db.String(50))

class Doktor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_soyad = db.Column(db.String(100))
    uzmanlik = db.Column(db.String(100))
    hastane = db.Column(db.String(100))

class Randevu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'))
    doktor_id = db.Column(db.Integer, db.ForeignKey('doktor.id'))
    tarih = db.Column(db.String(10))
    saat = db.Column(db.String(5))
    sikayet = db.Column(db.Text)
    kullanici = db.relationship('Kullanici', backref=db.backref('randevular', lazy=True))
    doktor = db.relationship('Doktor', backref=db.backref('randevular', lazy=True))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/kayit_ol', methods=['GET', 'POST'])
def kayit_ol():
    if request.method == 'POST':
        ad_soyad = request.form['ad_soyad']
        email = request.form['email']
        sifre = request.form['sifre']
        il = request.form['il']
        ilce = request.form['ilce']
        yeni_kullanici = Kullanici(ad_soyad=ad_soyad, email=email, sifre=sifre, il=il, ilce=ilce)
        db.session.add(yeni_kullanici)
        db.session.commit()
        flash('Kayıt başarılı!', 'success')
        return redirect(url_for('giris_yap'))
    return render_template('kayit_ol.html')

@app.route('/giris_yap', methods=['GET', 'POST'])
def giris_yap():
    if request.method == 'POST':
        email = request.form['email']
        sifre = request.form['sifre']
        kullanici = Kullanici.query.filter_by(email=email, sifre=sifre).first()
        if kullanici:
            session['kullanici_id'] = kullanici.id
            return redirect(url_for('randevu_al'))
        else:
            flash('Geçersiz email veya şifre!', 'danger')
    return render_template('giris_yap.html')

@app.route('/randevu_al', methods=['GET', 'POST'])
def randevu_al():
    if 'kullanici_id' not in session:
        return redirect(url_for('giris_yap'))
    if request.method == 'POST':
        il = request.form['il']
        ilce = request.form['ilce']
        sikayet = request.form['sikayet']
        tarih = request.form['tarih']
        saat = request.form['saat']
        kullanici_id = session['kullanici_id']
        doktor_id = 1  # Burada doktor seçim işlemi dinamik olarak yapılmalı
        yeni_randevu = Randevu(kullanici_id=kullanici_id, doktor_id=doktor_id, tarih=tarih, saat=saat, sikayet=sikayet)
        db.session.add(yeni_randevu)
        db.session.commit()
        flash('Randevunuz eklendi!', 'success')
        return redirect(url_for('randevularim'))
    return render_template('randevu_al.html')

@app.route('/randevularim')
def randevularim():
    if 'kullanici_id' not in session:
        return redirect(url_for('giris_yap'))
    kullanici_id = session['kullanici_id']
    randevular = Randevu.query.filter_by(kullanici_id=kullanici_id).all()
    return render_template('randevularim.html', randevular=randevular)

@app.route('/cikis_yap')
def cikis_yap():
    session.pop('kullanici_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('hastane_sistemi.db'):
            db.create_all()
    app.run(debug=True)
