# /// script
# requires-python = ">=3.11"
# dependencies = ["yfinance>=0.2.65"]
# ///
"""拉取公司财报三表 + 关键指标（yfinance）。用于一手来源的交叉验证。"""
import argparse, json, sys
import yfinance as yf
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)

ap = argparse.ArgumentParser()
ap.add_argument("ticker")
ap.add_argument("--stmt", default="all", choices=["all","is","bs","cf"])
a = ap.parse_args()

t = yf.Ticker(a.ticker)
print(f"===== {a.ticker} 基本信息 =====")
try:
    info = t.info
    for k in ["longName","currency","financialCurrency","sharesOutstanding","marketCap",
              "trailingPE","forwardPE","priceToSalesTrailing12Months","enterpriseValue",
              "enterpriseToEbitda","beta","totalCash","totalDebt","debtToEquity","fiftyTwoWeekHigh","fiftyTwoWeekLow"]:
        if k in info: print(f"  {k}: {info[k]}")
except Exception as e:
    print("  info 失败:", e)

def show(name, df, ncols=5):
    print(f"\n===== {name}（单位：报表币种，通常百万） =====")
    if df is None or df.empty:
        print("  未获取到"); return
    print(df.iloc[:, :ncols].to_string())

if a.stmt in ("all","is"): show("利润表 Income Statement", t.income_stmt)
if a.stmt in ("all","cf"): show("现金流量表 Cash Flow", t.cashflow)
if a.stmt in ("all","bs"): show("资产负债表 Balance Sheet", t.balance_sheet)
