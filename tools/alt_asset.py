#!/usr/bin/env python3
"""另类资产对组合的影响 + QDII 溢价计算（第 16 章配套工具，仅用标准库）

用法：
    # 在「股 40 / 债 60」里加入不同比例黄金，看组合波动和回撤
    python3 tools/alt_asset.py mix --stock 40 --alt-mu 3 --alt-sigma 15 --stock-corr 0.1 --bond-corr 0.1
    python3 tools/alt_asset.py mix --stock 40 --alt-mu 6 --alt-sigma 18 --stock-corr 0.7 --bond-corr 0.2

    # QDII 场内溢价：净值 1.20，场内价 1.32
    python3 tools/alt_asset.py premium --nav 1.20 --price 1.32
"""
import argparse
import math
import random

MS, SS, MB, SB = 0.08, 0.20, 0.03, 0.04


def sim(w_s, w_a, a, rng, n=2000, years=10):
    w_b = 1 - w_s - w_a
    vol = math.sqrt((w_s * SS) ** 2 + (w_b * SB) ** 2 + (w_a * a.alt_sigma) ** 2
                    + 2 * w_s * w_b * a.sc_corr * SS * SB
                    + 2 * w_s * w_a * a.alt_corr_stock * SS * a.alt_sigma
                    + 2 * w_b * w_a * a.alt_corr_bond * SB * a.alt_sigma)
    finals, dds = [], []
    for _ in range(n):
        v, peak, dd = 1.0, 1.0, 0.0
        for _ in range(years * 12):
            rs = rng.gauss(MS / 12, SS / math.sqrt(12))
            rb = rng.gauss(MB / 12, SB / math.sqrt(12))
            ra = rng.gauss(a.alt_mu / 100 / 12, a.alt_sigma / 100 / math.sqrt(12))
            r = w_s * rs + w_b * rb + w_a * ra
            v *= 1 + r
            peak = max(peak, v)
            dd = max(dd, 1 - v / peak)
        finals.append(v)
        dds.append(dd)
    finals.sort()
    return vol, sum(dds) / len(dds), (sum(finals) / len(finals)) ** 0.1 - 1, finals[int(n * 0.05)]


def cmd_mix(a) -> None:
    a.alt_sigma /= 100
    a.alt_corr_stock = a.stock_corr
    a.alt_corr_bond = a.bond_corr
    a.sc_corr = 0.0
    print(f"基准：股 {a.stock}% / 债 {100 - a.stock}%，股 8%/20%、债 3%/4%")
    print(f"加入资产：收益 {a.alt_mu}%、波动 {a.alt_sigma * 100:g}%、与股相关 {a.stock_corr}、与债相关 {a.bond_corr}")
    print(f"  {'它的比例':>6} {'股票比例':>6} {'组合波动':>8} {'平均最大回撤':>10} {'平均年化':>8} {'最差5%期末':>10}")
    for pct in (0, 5, 10, 15, 20, 30):
        w_a = pct / 100
        w_s = (1 - w_a) * a.stock / 100
        rng = random.Random(13)
        vol, dd, cagr, p05 = sim(w_s, w_a, a, rng)
        print(f"  {pct:>7}% {w_s * 100:>7.1f}% {vol * 100:>9.1f}% {dd * 100:>11.1f}% {cagr * 100:>9.2f}% {p05:>11.2f}")


def cmd_premium(a) -> None:
    p = a.price / a.nav - 1
    print(f"净值 {a.nav:.3f}，场内价 {a.price:.3f}，溢价 {p:.2%}")
    print(f"  此刻买入，如果溢价回到 0，价格要跌 {p / (1 + p):.2%}，等于白亏这么多")
    for nv, nn in ((p - 0.05, a.nav), (p + 0.05, a.nav)):
        print(f"  溢价 {nv:.1%} 时对应价格 {nn * (1 + nv):.3f}")


def main() -> None:
    p = argparse.ArgumentParser(description="另类资产与 QDII 溢价")
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("mix")
    m.add_argument("--stock", type=float, default=40)
    m.add_argument("--alt-mu", type=float, default=3)
    m.add_argument("--alt-sigma", type=float, default=15)
    m.add_argument("--stock-corr", type=float, default=0.1)
    m.add_argument("--bond-corr", type=float, default=0.1)
    q = sub.add_parser("premium")
    q.add_argument("--nav", type=float, required=True)
    q.add_argument("--price", type=float, required=True)
    a = p.parse_args()
    cmd_mix(a) if a.cmd == "mix" else cmd_premium(a)


if __name__ == "__main__":
    main()
