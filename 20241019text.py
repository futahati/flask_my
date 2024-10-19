from flask import Flask, render_template
from twsescrape import show_today, get_holidays


app = Flask(__name__)


@app.route("/<date>")
def day(date):
    date = show_today()

    print(date)

    return render_template("./20241019text.html", date=date)


app.run(debug=True)
