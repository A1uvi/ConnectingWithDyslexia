import os
from uuid import uuid4
from flask import Flask, request, render_template, send_from_directory, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import (StringField,SubmitField,SelectField,IntegerField,TextAreaField)
from wtforms.validators import DataRequired
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\alvia\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

__author__ = 'ibininja'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jgejihtgiohtonfgjegop'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route("/translate")
def index():
    return render_template("upload.html")

@app.route("/done-translating", methods=["POST"])
def upload():
    target = os.path.join(APP_ROOT, 'images/')
    # target = os.path.join(APP_ROOT, 'static/')
    print(target)
    if not os.path.isdir(target):
            os.mkdir(target)
    else:
        print("Couldn't create upload directory: {}".format(target))
    print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        filename = upload.filename
        destination = "/".join([target, filename])
        upload.save(destination)

    text = pytesseract.image_to_string(destination, lang='eng')         
    text = text.encode("gbk", 'ignore').decode("gbk", "ignore")
    return render_template("complete_display_image.html", image_name=filename, text=text)

@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

@app.route('/')
def home():
    return render_template("home.html")

class preGradebookForm(FlaskForm):
    style={'class': 'ourClasses', 'style': 'width:50%;'}
    numAss = StringField('How many assignments do you have? ',validators=[DataRequired()],render_kw=style)
    aim = SelectField(u'What grade are you aiming for?',
                        choices=[('59.5', '60 - 70%'), ('69.5', '71 - 80%'), ('79.5', '81 - 90%'),
                        ('89.5', '91 - 100%')], validators=[DataRequired()],render_kw=style)
    submit = SubmitField('Submit')

dicts = {}
aiming = {}
@app.route('/academic-support',methods=['GET','POST'])
def academic_support():
    form = preGradebookForm()
    if form.validate_on_submit():
        session['numAss'] = form.numAss.data
        session['aim'] = form.aim.data
        aiming[1] = session['aim']
        dicts.clear()
        keys = range(1,int(session['numAss'])+1)
        for i in keys:
            dicts[i] = i
        print(dicts)
        return redirect(url_for("points",num=session['numAss']))
    
    return render_template('academic-support.html', form=form)

class gradebookForm(FlaskForm):
    style={'class': 'ourClasses', 'style': 'width:50%;'}
    assName = StringField('What is this assignment called?',validators=[DataRequired()],render_kw=style)
    outof = IntegerField('How many points could you get?',validators=[DataRequired()],render_kw=style)
    got = IntegerField('How many points did you get?',validators=[DataRequired()],render_kw=style)
    submit = SubmitField('Submit')

@app.route('/points/<num>',methods=['GET','POST'])
def points(num):
    form = gradebookForm()
    num = int(num)
    if form.validate_on_submit():
        session['assName'] = form.assName.data
        session['outof'] = form.outof.data
        session['got'] = form.got.data
        trash = dicts.pop(num)
        dicts[session['assName']] = [(session['got']),(session['outof'])]
        print(dicts)
        num = num - 1
        if num > 0:
            return redirect(url_for("points",num=num))
        else:
            return redirect(url_for("gradecalc"))
    else:
        return render_template('mainform.html', form=form)

@app.route('/gradecalc')
def gradecalc():
    print(aiming)
    sum = 0
    total = 0
    keyList = list(dicts.keys())
    for x in range(len(keyList)):
        sum = sum + dicts[keyList[x]][0]
        total = total + dicts[keyList[x]][1]
    avg = sum/total
    print(avg)


    lowering_list = []
    for i in range(len(keyList)):
        if  ((dicts[keyList[i]][0]/dicts[keyList[i]][1]) < avg):
            lowering_list.append(list(dicts.keys())[i])
    print(lowering_list)

    return render_template('grade-calc.html',avg=avg*100,aiming=float(aiming[1]),badlist=lowering_list,mylist=keyList,dicts=dicts)

class emailForm(FlaskForm):
    style={'class': 'ourClasses', 'style': 'width:50%;'}
    addTo = StringField('Who do you want to email? ',validators=[DataRequired()],render_kw=style)
    sub = StringField('What should the subject be? ',validators=[DataRequired()],render_kw=style)
    message = TextAreaField('Enter message: ',validators=[DataRequired()],render_kw=style)
    submit = SubmitField('Submit')

@app.route('/connect', methods=['GET', 'POST'])
def connect():
    form = emailForm()
    if form.validate_on_submit():
        session['addTo'] = form.addTo.data
        session['sub'] = form.message.data
        session['message'] = form.message.data
        return redirect(url_for("connected"))
    
    return render_template('connect.html', form=form)

@app.route('/connected')
def connected():
    return render_template('connected.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404error.html'), 404

if __name__ == "__main__":
    app.run(port=4555)

