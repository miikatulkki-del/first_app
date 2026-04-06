from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_scss import Scss
from datetime import datetime
from plotnine import ggplot, aes, geom_bar, labs, coord_flip, theme_classic, geom_col
import pandas as pd

# My App
app = Flask(__name__)
Scss(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db = SQLAlchemy(app)

# Data Class ~ Row of Data
class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable = False)
    complete = db.Column(db.Integer, default = 0)
    created = db.Column(db.DateTime, default = datetime.utcnow)
    maara = db.Column(db.Integer, default = 0)


    def __repr__(self) -> str:
        return f"Task {self.id}"

#Home Page
@app.route("/",methods=["POST","GET"])
def index():
    #Add a task
    if request.method == "POST":
        current_task = request.form['content']
        kauanko_kestaa = request.form['maara']
        new_task = MyTask(content = current_task,maara=kauanko_kestaa)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"ERROR:{e}")
            return f"ERROR:{e}"
        
    
    #See all current tasks
    else:
        tekemattomat_aika = 0
        tehdyt_aika = 0
        tasks = MyTask.query.order_by(MyTask.created).all()
        for task in tasks:
            if task.complete == 0:
                tekemattomat_aika += task.maara
            else:
                tehdyt_aika += task.maara 
        data = {
        "status": ["tehty", "tekemättä"],
        "aika": [tehdyt_aika,tekemattomat_aika]
        }
        #load data into a DataFrame object:
        df = pd.DataFrame(data)
        return render_template('index.html', tasks=tasks, tekemattomat_aika=tekemattomat_aika,tehdyt_aika=tehdyt_aika,labels = df.status, aika = df.aika)

#Teen plotin hihii
data = {
    "status": ["tehty", "tekemättä"],
    "aika": [60,40]
}
#load data into a DataFrame object:
df = pd.DataFrame(data)
# See how long all the tasks take


# Delete an item
@app.route("/delete/<int:id>")
def delete(id:int):
    delete_task = MyTask.query.get_or_404(id)
    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return f"ERROR {e}"
    
# Mark as done
@app.route("/done/<int:id>")
def done(id:int):
    task = MyTask.query.get_or_404(id)
    task.complete = 1
    try:
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return f"Error: {e}"

# Edit an item
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id:int):
    task = MyTask.query.get_or_404(id)
    if request.method == "POST":
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return f"Error: {e}"
    else:
        return render_template('edit.html',task=task)

kokonaisaika = 0

if __name__ in "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True) 
