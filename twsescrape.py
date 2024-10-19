import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

# 這裡是外部模組，下方函式提供給main.py使用


# 20241015新增TWES臺灣證券交易所_每日收盤行情(ETF)_HTML版
def get_twse():
    """
    20241019新增 holidays
    但是，股市截止時間未設定完成
    """
    try:
        holidays = get_holidays()
        # date = datetime.datetime.now().strftime("%Y%m%d")
        # 測試用
        date = "20241018"

        datas = None
        title = None
        if date not in holidays:
            url = (
                "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date="
                + date
                + "&type=0099P&response=html"
            )
            resp = requests.get(url)
            soup = BeautifulSoup(resp.text, "lxml")
            title = soup.find("thead").find("div").text
            ths = [th.text for th in soup.find("thead").find_all("th")[1:]]
            tds = [
                [td.text for td in tr.find_all("td")]
                for tr in soup.find("tbody").find_all("tr")
            ]

            datas = pd.DataFrame(tds, columns=ths)
            # 將新增欄位（漲跌價），並指定欄位位置（9） → 漲跌價 = 漲跌(+/-) + 漲跌價差
            datas.insert(
                loc=9, column="漲跌價", value=datas["漲跌(+/-)"] + datas["漲跌價差"]
            )
            # 刪除 漲跌(+/-) 、 漲跌價差、本益比 這 3 個欄位。iloc的欄位置→10,11,16；inplace=True→改變原始資料(直接覆寫)
            datas.drop(datas.iloc[:, [10, 11, 16]], axis=1, inplace=True)

        return datas, title

    except Exception as e:
        print(e)

    return None, None


# 將 twse 的資訊，以「成交股數」排序，並取得最高成交股數的前10名資訊
def show_twse():
    datas, title = get_twse()

    # 針對成交股數轉換數值型態，先清除逗號，再使用eval
    datas["成交股數"] = datas["成交股數"].apply(lambda x: eval(x.replace(",", "")))
    # 以「成交股數」排序，並取得最高成交股數的前10名資訊
    datas1 = datas.sort_values("成交股數", ascending=False)[:10]
    # 刪除「10:14」欄(axis=1)
    datas1.drop(datas1.iloc[:, 10:14], axis=1, inplace=True)

    columns = datas1.columns
    values = datas1.values

    return columns, values


# [twse]取得設定完的 json 格式
def show_twseetf_json():
    columns, values = show_twse()

    xdata = [value[0] + value[1] for value in values]
    # value[9] → 漲跌價
    ydata = [value[9] for value in values]

    json_data = {"證券名稱": xdata, "漲跌價": ydata}

    # 證券代號
    xdata2 = [value[0] for value in values]
    # 開盤、收盤、最高、最低
    y1 = [value[5] for value in values]
    y2 = [value[8] for value in values]
    y3 = [value[6] for value in values]
    y4 = [value[7] for value in values]

    json_data2 = {"證券代號": xdata2, "開盤": y1, "收盤": y2, "最高": y3, "最低": y4}

    return json_data, json_data2


# [twse]非數值型的資料轉為 None，再 dropna掉
def convert_value(value):
    try:
        return eval(value)
    except:
        return None


# 取得當日時間
def show_today():

    day = datetime.datetime.now()
    weekday = {0: "日", 1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六"}
    today = day.strftime("%Y/%m/%d  %p %H:%M")
    print(today)
    # 加一天
    tomorrow = (day + datetime.timedelta(days=1)).strftime("%Y%m%d")
    print(tomorrow)
    # 減一天
    yesterday = (day + datetime.timedelta(days=-1)).strftime("%Y%m%d")
    print("yesterday=" + yesterday)

    return today


# 取得股市交易日
def get_tradingDay():
    holidays = get_holidays()
    date = datetime.datetime.now().strftime("%Y%m%d")

    day = datetime.datetime.now()
    Specifytime = datetime.datetime.strptime("13:30", "%H:%M").time()

    if date not in holidays:
        timenow = datetime.datetime.now().time()

        # 判斷時間是否在 13:30 前，若是，取得前一天日期，否則取當天日期
        if timenow < Specifytime:
            TradingDay = (day + datetime.timedelta(days=-1)).strftime("%Y%m%d")
        else:
            TradingDay = day.strftime("%Y%m%d")

        return TradingDay


# 取得臺灣放假日(文字型態)，排除掉「補行上班日」
def get_holidays():
    # 政府資料開放平臺/政府行政機關辦公日曆表
    url = "https://data.ntpc.gov.tw/api/datasets/308dcd75-6434-45bc-a95f-584da4fed251/csv/file"
    resp = requests.get(url)
    if resp.status_code == 200:
        """
        pd.read_csv(StringIO())直接讀取csv所在網址的資料
        usecols 參考：https://www.cnblogs.com/traditional/p/12514914.html
        usecols 取得指定的 columns/欄資料/直欄資料
        low_memory = False → 讀取的欄位有混合類型的資料，將low_memory參數設置為False 可以忽略警告。
        """
        datas = pd.read_csv(StringIO(resp.text), usecols=[0, 3], low_memory=False)
        # 刪除「補行上班日」：先取得isholiday為「否」的index，再進行刪除。
        datas.drop(datas.groupby("isholiday").get_group("否").index, inplace=True)
        # 將 date 欄位轉換為文字型態，並將資料回存，直接將「isholiday」欄資料刪除
        datas = datas["date"].apply(lambda x: str(x))

    else:
        print("資料取得失敗。", resp.status_code)

    holidays = datas.values

    return holidays


# 本地端測上方程式碼。測試時，若有其他 server 在運行，請先其他的 server 關閉。
if __name__ == "__main__":
    print(get_twse())
