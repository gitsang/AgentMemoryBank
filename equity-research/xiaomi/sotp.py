#!/usr/bin/env python3
"""小米集团 SOTP（分部加总）估值 —— 正向 + 反向。

口径纪律
- 分部收入/毛利率 = H1 2026 实际披露（RMB 百万）× 2.10 年化；合计须贴合一致预期 FY2026E。
- 倍数锚定真实可比公司（Lenovo 0992.HK / BYD 1211.HK / Li Auto LI），不凭空设定。
- 净现金 = 核心口径 RMB 86.585bn。
- 反向 SOTP：固定现价，解出现价隐含的分部倍数，与可比锚对比。

单位：RMB 十亿（bn）；输出 HKD/股。现价 27.08 HKD，HKD/CNY 0.8524。
"""
import json
import os

SHARES = 25.7947          # bn 股，HKEX 月报表 2026-09-30（不含库存股）
NET_CASH = 86.585         # bn RMB，核心口径
HKD_CNY = 0.8524
PRICE_HKD = 27.08
CONSENSUS_FY26 = 437.3    # bn RMB
FY_FACTOR = 2.10

# H1 2026 实际（RMB 百万）
H1 = {
    "智能手机":   {"rev": 86392.0, "gm": 0.093},
    "IoT":       {"rev": 55959.2, "gm": 0.223},
    "其他硬件":   {"rev":  2439.8, "gm": -0.032},
    "互联网服务": {"rev": 18512.0, "gm": 0.764},
    "智能EV+AI": {"rev": 44760.3, "gm": 0.196},
}

# 可比锚（2026-10，来源见 market-data-20261015.md / stockanalysis / multiples.vc）
ANCHORS = {
    "Lenovo 0992.HK": {"ev_sales": 0.63, "note": "EV 452.2bn / 收入 715.1bn HKD，毛利率~15.5%"},
    "BYD 1211.HK":    {"ev_sales": 0.92, "note": "P/S 0.91 → 近似的 EV/收入"},
    "Li Auto LI":     {"ev_sales": 0.72, "note": "P/S 0.72"},
}

# 正向倍数区间：由可比锚 + 分部属性（增速/毛利率/亏损）推导
MULT = {
    "硬件（手机+IoT+其他）": {"ev_sales": (0.40, 0.65), "basis": "Lenovo 0.63x 为上限锚；手机份额下滑、毛利率 14.1% 低于 Lenovo 15.5%，取下沿"},
    "互联网服务":           {"ev_sales": (2.00, 3.00), "basis": "76.4% 毛利率但 H1 2026 仅 +1.9% 增长，不能给平台的 5x+；对标成熟高毛利软件"},
    "智能EV+AI":           {"ev_sales": (0.70, 1.20), "basis": "Li Auto 0.72x / BYD 0.92x；小米 EV 仍亏损但增速更高，给到 BYD 之上"},
}


def build_segments():
    hw = {k: H1[k] for k in ("智能手机", "IoT", "其他硬件")}
    out = {}
    out["硬件（手机+IoT+其他）"] = {
        "rev": sum(v["rev"] for v in hw.values()) * FY_FACTOR / 1000,
        "gp": sum(v["rev"] * v["gm"] for v in hw.values()) * FY_FACTOR / 1000,
        "yoy": -12.9,  # H1 2026 智能手机×AIoT 分部同比（公司披露）
    }
    net = H1["互联网服务"]
    out["互联网服务"] = {"rev": net["rev"] * FY_FACTOR / 1000,
                        "gp": net["rev"] * net["gm"] * FY_FACTOR / 1000, "yoy": 1.9}
    ev = H1["智能EV+AI"]
    out["智能EV+AI"] = {"rev": ev["rev"] * FY_FACTOR / 1000,
                        "gp": ev["rev"] * ev["gm"] * FY_FACTOR / 1000, "yoy": 12.3}
    return out


def to_hkd(eq_bn):
    return eq_bn / SHARES / HKD_CNY


segs = build_segments()
total_rev = sum(s["rev"] for s in segs.values())
total_gp = sum(s["gp"] for s in segs.values())
mktcap = SHARES * PRICE_HKD * HKD_CNY
ev_now = mktcap - NET_CASH

print("=" * 88)
print("小米集团 SOTP · FY2026E · 单位 RMB 十亿")
print("=" * 88)
print(f"H1 2026 合计 {sum(v['rev'] for v in H1.values())/1000:.1f} bn × {FY_FACTOR} = {total_rev:.1f} bn")
print(f"一致预期 FY2026E {CONSENSUS_FY26} bn → 偏离 {(total_rev/CONSENSUS_FY26-1):+.1%}")
print()
print("【可比锚】")
for name, a in ANCHORS.items():
    print(f"  {name:<20} EV/收入 {a['ev_sales']:.2f}x   {a['note']}")
print()
print(f"{'分部':<22}{'收入':>7}{'同比':>8}{'毛利率':>8}{'毛利':>7}")
for name, s in segs.items():
    print(f"{name:<22}{s['rev']:>7.1f}{s['yoy']:>+7.1f}%{s['gp']/s['rev']:>8.1%}{s['gp']:>7.1f}")
print(f"{'合计':<22}{total_rev:>7.1f}{'':>8}{total_gp/total_rev:>8.1%}{total_gp:>7.1f}")
print()

# ---------- 正向 ----------
lo_eq = hi_eq = 0.0
print("【正向 SOTP】")
print(f"{'分部':<22}{'基数(收入)':>10}{'倍低':>7}{'倍高':>7}{'EV低':>8}{'EV高':>8}")
for name, s in segs.items():
    m_lo, m_hi = MULT[name]["ev_sales"]
    v_lo, v_hi = s["rev"] * m_lo, s["rev"] * m_hi
    lo_eq += v_lo; hi_eq += v_hi
    print(f"{name:<22}{s['rev']:>10.1f}{m_lo:>7.2f}{m_hi:>7.2f}{v_lo:>8.1f}{v_hi:>8.1f}")
print(f"{'分部EV':<22}{'':>10}{'':>7}{'':>7}{lo_eq:>8.1f}{hi_eq:>8.1f}")
print(f"{'+ 净现金':<22}{'':>10}{'':>7}{'':>7}{NET_CASH:>8.1f}{NET_CASH:>8.1f}")
print(f"{'= 权益':<22}{'':>10}{'':>7}{'':>7}{lo_eq+NET_CASH:>8.1f}{hi_eq+NET_CASH:>8.1f}")
fw_lo, fw_hi = to_hkd(lo_eq + NET_CASH), to_hkd(hi_eq + NET_CASH)
print(f"→ 每股 HKD  {fw_lo:.1f} – {fw_hi:.1f}   （现价 {PRICE_HKD}，隐含 {(fw_lo/PRICE_HKD-1):+.0%} ~ {(fw_hi/PRICE_HKD-1):+.0%}）")
print()

# ---------- 反向 ----------
print("【反向 SOTP】现价隐含的分部倍数")
print(f"现价市值 {mktcap:.1f} bn RMB | EV = 市值 + 净现金 = {ev_now:.1f} bn")
print(f"拆解：EV = Σ(分部收入 × 隐含倍数)。除『硬件』外，其余分部倍数固定于可比锚中枢，解出硬件隐含倍数。")
print()
fixed = {"互联网服务": 2.50, "智能EV+AI": 0.95}
implied_hw = (ev_now - sum(segs[k]["rev"] * m for k, m in fixed.items())) / segs["硬件（手机+IoT+其他）"]["rev"]
print(f"{'分部':<22}{'收入':>8}{'隐含倍数':>10}{'隐含EV':>9}{'倍数来源':>14}")
for name, s in segs.items():
    if name in fixed:
        m = fixed[name]; src = "可比锚中枢"
    else:
        m = implied_hw; src = "★解出"
    print(f"{name:<22}{s['rev']:>8.1f}{m:>10.2f}{s['rev']*m:>9.1f}{src:>14}")
print(f"{'合计':<22}{total_rev:>8.1f}{'':>10}{ev_now:>9.1f}")
print()
print(f"★ 硬件隐含倍数 {implied_hw:.2f}x EV/收入，vs Lenovo {ANCHORS['Lenovo 0992.HK']['ev_sales']:.2f}x、")
print(f"  BYD {ANCHORS['BYD 1211.HK']['ev_sales']:.2f}x → 现价给硬件的是 **{implied_hw/ANCHORS['Lenovo 0992.HK']['ev_sales']:.1f} 倍于 Lenovo**")
print()
# 反算：若硬件只给 Lenovo 的 0.63x，需要互联网服务给多少
resid = ev_now - segs["硬件（手机+IoT+其他）"]["rev"] * 0.63 - segs["智能EV+AI"]["rev"] * 0.95
need_net = resid / segs["互联网服务"]["rev"]
print(f"※ 对称检验：若硬件按 Lenovo 0.63x、EV 按 0.95x，则互联网服务须给 **{need_net:.1f}x EV/收入**")
print(f"  （对标：Tencent P/S 约 5-6x。{need_net:.1f}x 对一家 +1.9% 增长的业务 = 极难成立）")

json.dump({"shares_bn": SHARES, "net_cash_bn": NET_CASH, "hkd_cny": HKD_CNY, "price_hkd": PRICE_HKD,
           "segments_fy2026e": segs, "anchors": ANCHORS, "multiples": MULT,
           "forward": {"lo_hkd": fw_lo, "hi_hkd": fw_hi},
           "reverse": {"implied_hw_ev_sales": implied_hw, "net_needed_if_hw_at_lenovo": need_net,
                       "fixed_assumed": fixed},
           "market_cap_bn": mktcap, "ev_bn": ev_now},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "work", "sotp_output.json"), "w"),
          ensure_ascii=False, indent=1)
