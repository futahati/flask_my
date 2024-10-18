from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 這裡是外部模組，下方函式提供給main.py使用


# 取得[histock]的 ETF 表格資訊
def get_etfstocks():
    url = "https://histock.tw/stock/etf.aspx"
    try:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "lxml")
        trs = soup.find(id="etfitem1_gv").find_all("tr")

        # 將資料轉成「二維」！！
        datas = []

        for tr in trs:
            data = []
            for th in tr.find_all("th"):
                data.append(th.text.strip())

            for td in tr.find_all("td"):
                data.append(td.text.strip())

            datas.append(data)

        return datas

    except Exception as e:
        print(e)

    return None


# 將[histock]的資訊，進階為排序資訊，以「漲跌」為依據
def show_etfstocks(sort=False, ascending=False):
    try:
        datas = get_etfstocks()

        df = pd.DataFrame(datas[1:], columns=datas[0])
        # df["漲跌"] = df["漲跌"].apply(lambda x: eval(x))
        df["漲跌"] = df["漲跌"].apply(convert_value)
        # 移除所有None的數據
        df = df.dropna()

        if sort:
            # 排序ascending=False：由大至小，反儲回 df / ascending=True 由小至大
            df = df.sort_values("漲跌", ascending=ascending)

        columns = df.columns
        values = df.values

        return columns, values

    except Exception as e:
        print(e)

    return None, "404錯誤"


# [histock]排序時，發現非數值型，所以單獨寫一個函式，將資料全部eval
def convert_value(value):
    try:
        return eval(value)
    except:
        return None


# [histock]取得設定完的 json 格式
def show_etf_json():
    columns, values = show_etfstocks()

    xdata = [value[0] for value in values]
    # value[2] → 成交價
    ydata = [value[2] for value in values]

    json_data = {"x": xdata, "y": ydata}

    return json_data


# [histock]非數值型的資料轉為 None，再 dropna掉
def convert_value(value):
    try:
        return eval(value)
    except:
        return None


# 取得當日時間
def show_today():

    # today = datetime.now()
    weekday = {0: "日", 1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六"}
    today = datetime.now().strftime("%Y/%m/%d  %p %H:%M")

    return today


# 本地端測上方程式碼。測試時，若有其他 server 在運行，請先其他的 server 關閉。
if __name__ == "__main__":
    print(show_etfstocks())
