# /// script
# requires-python = ">=3.11"
# dependencies = ["yfinance>=0.2.65"]
# ///
"""港股/A股/美股 行情与财报直取。腾讯接口优先（稳定），yfinance 兜底。"""
import argparse, json, sys, urllib.request

def tencent(codes):
    url = "https://qt.gtimg.cn/q=" + ",".join(codes)
    raw = urllib.request.urlopen(url, timeout=15).read().decode("gbk", "ignore")
    out = {}
    for line in raw.strip().split("\n"):
        if "=" not in line: continue
        key, val = line.split("=", 1)
        f = val.strip().strip(';').strip('"').split("~")
        if len(f) < 35: continue
        out[f[2]] = {"name": f[1], "code": f[2], "price": float(f[3]), "prev_close": float(f[4]),
                     "open": float(f[5]), "volume": float(f[6]), "change": float(f[31]),
                     "change_pct": float(f[32]), "high": float(f[33]), "low": float(f[34]),
                     "time": f[30], "pe_ttm": f[39] if len(f) > 39 else None,
                     "mktcap_100m": f[45] if len(f) > 45 else None,
                     "52w_high": f[48] if len(f) > 48 else None,
                     "52w_low": f[49] if len(f) > 49 else None}
    return out

def yahoo(symbols):
    """yfinance 兜底（含财务报表）。腾讯接口失败时使用。"""
    import yfinance as yf
    out = {}
    for s in symbols:
        t = yf.Ticker(s)
        fi = t.fast_info
        out[s] = {"price": fi.last_price, "prev_close": fi.previous_close,
                  "market_cap": fi.market_cap, "year_high": fi.year_high,
                  "year_low": fi.year_low, "currency": fi.currency}
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("codes", nargs="+", help="如 hk01810 hk09988 sh600519 usAAPL")
    ap.add_argument("--kline", help="取历史日线，如 hk01810")
    ap.add_argument("--limit", type=int, default=400)
    ap.add_argument("--yahoo", action="store_true", help="改用 yfinance（含财务报表）")
    a = ap.parse_args()
    if a.yahoo:
        print(json.dumps(yahoo(a.codes), ensure_ascii=False, indent=1, default=str))
        return
    if a.kline:
        url = f"https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get?param={a.kline},day,,,{a.limit},qfq"
        d = json.loads(urllib.request.urlopen(url, timeout=20).read())["data"][a.kline]
        rows = d.get("qfqday") or d.get("day")
        out = [{"date": r[0], "open": float(r[1]), "close": float(r[2]),
                "high": float(r[3]), "low": float(r[4]), "volume": float(r[5])} for r in rows]
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return
    print(json.dumps(tencent(a.codes), ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
