import sqlite3
from flask import Flask, render_template, redirect, session, flash
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


app = Flask(__name__)
app.debug = True
app.secret_key = 'be fe le me pes se veze'

cesta_db = 'chat.db'

class ZpravaForm(FlaskForm):
    zprava = TextAreaField(validators=[DataRequired()])

class PrihlasitForm(FlaskForm):
    uzivatel_jmeno = StringField('Uživatelské jméno', validators=[DataRequired()])
    heslo = PasswordField('Heslo', validators=[DataRequired(), Length(min=3, max=20)])
    submit = SubmitField('Přihlásit')

    def validate_heslo(self, heslo):
        if heslo.data != '123':
            raise ValidationError('Neplatné heslo.')

@app.route('/', methods=['GET', 'POST'])
def chat():
    form = ZpravaForm()
    if 'uzivatel_id' not in session:
        return redirect('/prihlasit')
    
    uzivatel_id = session['uzivatel_id']
    zprava = form.zprava.data

    con = sqlite3.connect(cesta_db)
    cur = con.cursor()
    res = cur.execute("SELECT uzivatele.uzivatel, zpravy.telo FROM zpravy \
                      INNER JOIN uzivatele ON zpravy.uzivatel_id=uzivatele.rowid")
    zpravy = res.fetchall()
    con.close()

    if form.validate_on_submit():
        con = sqlite3.connect(cesta_db)
        cur = con.cursor()
        cur.execute("INSERT INTO zpravy(uzivatel_id, telo) VALUES(?,?)", (uzivatel_id, zprava))
        con.commit()
        con.close()
        return redirect('/')
    
    return render_template('chat.html', form=form, zpravy=zpravy)

@app.route('/prihlasit', methods=['GET', 'POST'])
def prihlasit():
    form = PrihlasitForm()
    uzivatelske_jmeno = form.uzivatel_jmeno.data
    heslo = form.heslo.data

    if form.validate_on_submit():
        con = sqlite3.connect(cesta_db)
        cur = con.cursor()
        res = cur.execute("SELECT rowid FROM uzivatele WHERE uzivatel=?", (uzivatelske_jmeno,))
        session['uzivatel_id'] = res.fetchone()[0]
        con.close()
        return redirect('/')
    
    return render_template('prihlasit.html', form=form, heslo=heslo)

@app.route('/odhlasit')
def odhlasit():
    session.clear()
    return redirect('/prihlasit')

if __name__ == '__main__':
    app.run()
