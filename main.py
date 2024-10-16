from flask import Flask, render_template, request
from datetime import datetime
from scrape import (
    show_today,
    get_etfstocks,
    show_etfstocks,
    show_etf_json,
    get_twes,
    show_twse,
    show_twseetf_json,
)
import json


"""
前端、後端教學 [這裡是後端！！]
使用 「template 模版檥式 + jinja2 」
from flask import 增加→→ render_template, request
"""
app = Flask(__name__)


# template樣版名稱：index.html
# 注意前端、後端的網址不同
# 前端： http://127.0.0.1:5500/flaskmy/templates/index.html
# 後端： http://127.0.0.1:5000/
# date 與 today


# 首頁 index.html
@app.route("/")
def index():
    today = show_today()
    name = "外星來客"
    return render_template("index.html", date=today, name=name)


# 取得「Json 格式」的資料
books = {
    1: {
        "name": "Python book",
        "price": 299,
        "image_url": "https://im2.book.com.tw/image/getImage?i=https://www.books.com.tw/img/CN1/136/11/CN11361197.jpg&v=58096f9ck&w=348&h=348",
    },
    2: {
        "name": "Java book",
        "price": 399,
        "image_url": "https://im1.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/087/31/0010873110.jpg&v=5f7c475bk&w=348&h=348",
    },
    3: {
        "name": "C# book",
        "price": 499,
        "image_url": "https://im1.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/036/04/0010360466.jpg&v=62d695bak&w=348&h=348",
    },
}


# 書店 books.html
@app.route("/books")
def show_books():
    # print(books)  # 給後端看的
    today = show_today()
    # 取得每一本書的書名
    # 迴圈是給後端看的
    for key in books:
        print(books[key])

    return render_template("books.html", date=today, books=books)


# 只取得一本書的網址
@app.route("/book")
def show_book():
    return books[1]


# 重點：二維資料
# 爬取 EFT 表格(二維資料)爬蟲寫在外部 etf_scrape.py
# etf_histocks.html
@app.route("/etf", methods=["GET", "POST"])
def get_etf():
    today = show_today()
    # GET測試
    print(request.args)

    # POST測試。下方程式碼，以「POST」設定。
    print(request.form)

    datas = get_etfstocks()
    # 排序處理
    sort = False
    ascending = True

    # 判斷來自 GET 還是 POST
    if request.method == "POST":
        # 判斷是否按下排序按鈕
        if "sort" in request.form:
            sort = True
            # 取得 select 的 option
            ascending = True if request.form.get("sort") == "true" else False
            print(ascending)

    # etf爬蟲寫在外部 etf_scrape.py，再使用引用模組 (from + import)

    columns, values = show_etfstocks(sort, ascending)

    return render_template(
        "etf_histock.html", date=today, datas=datas, columns=columns, values=values
    )


# etf_chart.html 繪圖用
@app.route("/etf_data")
def etf_data():
    try:
        json_data = show_etf_json()

        return json.dumps(json_data, ensure_ascii=False)

    except Exception as e:
        print(e)

        return json.dumps({"result": "failure", "exception": str(e)})


# etf_chart.html 傳到前端
@app.route("/etf_chart")
def etf_chart():
    return render_template("etf_chart.html")


# 20241015新增TWES臺灣證券交易所_每日收盤行情(ETF)_HTML版
# [twse]etf_twse.html
@app.route("/etf_twse")
def get_twse_etf():
    today = show_today()

    # 一定要讀取函式裡所有 return ，無法單獨引用一個！！
    datas, title = get_twes()

    columns = datas.columns
    values = datas.values

    return render_template(
        "etf_twse.html", date=today, title=title, columns=columns, values=values
    )


# [twse]etf_chart.html 取得 json 格式，繪圖使用(不用開網頁給使用者)
# 將資訊寫在 twseetf_chart.html 裡
@app.route("/twseetf_data")
def twse_etf_data():
    try:
        json_data, json_data2 = show_twseetf_json()

        return json.dumps(json_data, ensure_ascii=False)

    except Exception as e:
        print(e)

        return json.dumps({"result": "failure", "exception": str(e)})


# 第 2 張圖表
@app.route("/twseetf_data2")
def twse_etf_data2():
    try:
        json_data, json_data2 = show_twseetf_json()

        return json.dumps(json_data2, ensure_ascii=False)

    except Exception as e:
        print(e)

        return json.dumps({"result": "failure", "exception": str(e)})


# [twse]twseetf_chart.html，取得函式裡的 json資訊，寫在 twseetf_chart.html 裡
@app.route("/twseetf_chart")
def twse_etf_chart():
    # 以成交股數排序，取得最高前20名資訊
    columns, values = show_twse()
    return render_template("twseetf_chart.html", columns=columns, values=values)


"""
server 開啟，需要 run
app.run()
Ctrl + C →關閉 server
為了不重複開／關 server，要帶 debug=True
app.run(debug=True)
上傳靜態網頁要改成下方程式碼
"""
app.run(host="0.0.0.0")
