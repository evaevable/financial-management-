#!/usr/bin/env python3
"""风险直觉模拟器（第 6 章配套工具，仅用标准库）

用法：
    # 回本需要涨多少
    python3 tools/risk_sim.py recover

    # 不同持有期下「亏钱的概率」（蒙特卡洛模拟，参数均为假设值）
    python3 tools/risk_sim.py horizon

    # 自定义：假设年化收益 8%、年化波动 20%
    python3 tools/risk_sim.py horizon --mu 8 --sigma 20

说明：
    - 模拟假设年收益服从正态分布、各年独立，这是简化模型，真实市场有厚尾和连续下跌，
      实际亏损概率与极端亏损幅度可能比模拟更糟。
    - 三类资产的默认参数只是教学用的「量级」假设，不代表任何产品的历史或预期表现。
    - 固定随机种子，保证每次运行结果一致。
"""
import argparse
import random

PRESETS = [
    ("偏现金类", 2.0, 0.5),
    ("偏债券类", 4.0, 4.0),
    ("偏股票类", 8.0, 20.0),
]


def cmd_recover(_a) -> None:
    print(f"{'亏损':>6} {'回本需要涨':>10}")
    for loss in (10, 20, 30, 40, 50, 70):
        need = 1 / (1 - loss / 100) - 1
        print(f"{loss:>5}% {need * 100:>10.1f}%")


def simulate(mu: float, sigma: float, years: int, n: int, rng: random.Random):
    finals, worst_dd = [], []
    for _ in range(n):
        v, peak, dd = 1.0, 1.0, 0.0
        for _ in range(years):
            r = max(-0.95, rng.gauss(mu, sigma))
            v *= 1 + r
            peak = max(peak, v)
            dd = max(dd, 1 - v / peak)
        finals.append(v)
        worst_dd.append(dd)
    finals.sort()
    loss_p = sum(1 for x in finals if x < 1) / n
    p05 = finals[int(n * 0.05)]
    return loss_p, p05, sum(worst_dd) / n


def cmd_horizon(a) -> None:
    rng = random.Random(42)
    presets = [("自定义", a.mu, a.sigma)] if a.mu is not None else PRESETS
    for name, mu, sigma in presets:
        print(f"{name}：假设年化收益 {mu}%、年化波动 {sigma}%（模拟 {a.n} 次）")
        print(f"  {'持有年数':>6} {'到期亏钱概率':>10} {'最差 5% 情形的期末值':>14} {'期间平均最大回撤':>12}")
        for years in (1, 3, 5, 10, 20):
            lp, p05, dd = simulate(mu / 100, sigma / 100, years, a.n, rng)
            print(f"  {years:>8} {lp * 100:>13.1f}% {p05:>20.2f} 倍 {dd * 100:>15.1f}%")
        print()


def main() -> None:
    p = argparse.ArgumentParser(description="风险直觉模拟器")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("recover")
    h = sub.add_parser("horizon")
    h.add_argument("--mu", type=float, help="假设年化收益（%%）")
    h.add_argument("--sigma", type=float, default=20, help="假设年化波动（%%）")
    h.add_argument("--n", type=int, default=20000, help="模拟次数")
    a = p.parse_args()
    cmd_recover(a) if a.cmd == "recover" else cmd_horizon(a)


if __name__ == "__main__":
    main()
