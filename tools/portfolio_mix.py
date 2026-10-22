#!/usr/bin/env python3
"""股债配置模拟器（第 12 章配套工具，仅用标准库）

用法：
    # 默认：股票类 / 债券类按 0%..100% 不同比例，持有 5 年
    python3 tools/portfolio_mix.py

    # 自定义假设参数与持有期
    python3 tools/portfolio_mix.py --stock-mu 8 --stock-sigma 20 --bond-mu 3 --bond-sigma 4 --corr 0 --years 10

    # 目标回撤：找出「平均最大回撤不超过 X%」的最高股票比例
    python3 tools/portfolio_mix.py --max-dd 20

说明：
    - 全部参数是教学用的假设量级，不代表任何指数或产品的历史或未来表现。
    - 按月模拟、每月再平衡回目标比例；收益服从正态分布、各月独立。
      真实市场有厚尾、连续下跌，股债相关性也会随时间变化（有时同跌），
      所以真实的坏情况可能比模拟更坏。
    - 固定随机种子 7，保证结果可复现。
"""
import argparse
import math
import random


def simulate(w, a, rng):
    ms, ss = a.stock_mu / 100 / 12, a.stock_sigma / 100 / math.sqrt(12)
    mb, sb = a.bond_mu / 100 / 12, a.bond_sigma / 100 / math.sqrt(12)
    rho = a.corr
    months = a.years * 12
    finals, dds, worst12 = [], [], []
    for _ in range(a.n):
        v, peak, dd = 1.0, 1.0, 0.0
        hist = [1.0]
        for _ in range(months):
            z1 = rng.gauss(0, 1)
            z2 = rho * z1 + math.sqrt(1 - rho * rho) * rng.gauss(0, 1)
            r = w * (ms + ss * z1) + (1 - w) * (mb + sb * z2)
            v *= 1 + r
            hist.append(v)
            peak = max(peak, v)
            dd = max(dd, 1 - v / peak)
        finals.append(v)
        dds.append(dd)
        worst12.append(min(hist[i + 12] / hist[i] - 1 for i in range(months - 11)))
    finals.sort()
    worst12.sort()
    cagr = (sum(finals) / a.n) ** (1 / a.years) - 1
    return (cagr, sum(1 for x in finals if x < 1) / a.n, finals[int(a.n * 0.05)],
            sum(dds) / a.n, worst12[int(a.n * 0.05)])


def main() -> None:
    p = argparse.ArgumentParser(description="股债配置模拟器")
    p.add_argument("--stock-mu", type=float, default=8)
    p.add_argument("--stock-sigma", type=float, default=20)
    p.add_argument("--bond-mu", type=float, default=3)
    p.add_argument("--bond-sigma", type=float, default=4)
    p.add_argument("--corr", type=float, default=0.0, help="股债相关系数（假设值）")
    p.add_argument("--years", type=int, default=5)
    p.add_argument("--n", type=int, default=3000)
    p.add_argument("--max-dd", type=float, help="可接受的平均最大回撤（%%）")
    a = p.parse_args()
    rng = random.Random(7)

    print(f"假设：股票类 收益 {a.stock_mu}% 波动 {a.stock_sigma}%；债券类 收益 {a.bond_mu}% 波动 {a.bond_sigma}%；"
          f"相关系数 {a.corr}；持有 {a.years} 年，每月再平衡")
    print(f"  {'股票比例':>6} {'年化波动':>8} {'到期亏钱概率':>10} {'最差5%期末':>10} {'平均最大回撤':>10} {'最差5%的一年':>10}")
    best = None
    for pct in range(0, 101, 10):
        w = pct / 100
        vol = math.sqrt((w * a.stock_sigma) ** 2 + ((1 - w) * a.bond_sigma) ** 2
                        + 2 * w * (1 - w) * a.corr * a.stock_sigma * a.bond_sigma)
        _, lp, p05, dd, w12 = simulate(w, a, rng)
        print(f"  {pct:>7}% {vol:>9.1f}% {lp * 100:>12.1f}% {p05:>11.2f} 倍 {dd * 100:>11.1f}% {w12 * 100:>+12.1f}%")
        if a.max_dd is not None and dd * 100 <= a.max_dd:
            best = pct
    if a.max_dd is not None:
        print(f"\n平均最大回撤不超过 {a.max_dd}% 的最高股票比例：{best}%" if best is not None
              else f"\n没有任何比例的平均最大回撤低于 {a.max_dd}%")


if __name__ == "__main__":
    main()
