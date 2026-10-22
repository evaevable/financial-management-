#!/usr/bin/env python3
"""定投 vs 一次性投入：用几条假设的价格路径建立直觉（第 11 章配套工具，仅用标准库）

用法：
    python3 tools/dca_sim.py                    # 五条假设路径，每月投 1000，共 36 个月
    python3 tools/dca_sim.py --monthly 2000 --months 24

说明：
    - 价格路径都是人为构造的「形状」，不是任何指数的真实走势，只用来理解机制。
    - 一次性投入：第 0 个月一次投入「每月金额 x 月数」；定投：每月初投入「每月金额」。
    - 均在最后一个月末按当时价格计算市值，不计费用和分红。
"""
import argparse
import math


def paths(n: int):
    def lin(a, b, k, m):
        return a + (b - a) * k / m

    half = n // 2
    return {
        "一路上涨 1→2": [lin(1, 2, k, n) for k in range(n + 1)],
        "一路下跌 1→0.5": [lin(1, 0.5, k, n) for k in range(n + 1)],
        "先跌后回 1→0.5→1": [lin(1, 0.5, k, half) if k <= half else lin(0.5, 1, k - half, n - half) for k in range(n + 1)],
        "先涨后回 1→1.5→1": [lin(1, 1.5, k, half) if k <= half else lin(1.5, 1, k - half, n - half) for k in range(n + 1)],
        "原地震荡 ±20%": [1 + 0.2 * math.sin(2 * math.pi * k / 12) for k in range(n + 1)],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="定投 vs 一次性投入")
    p.add_argument("--monthly", type=float, default=1000)
    p.add_argument("--months", type=int, default=36)
    a = p.parse_args()
    total = a.monthly * a.months
    print(f"共投入 {total:,.0f}：一次性在第 0 月投入，或每月 {a.monthly:,.0f} 连投 {a.months} 个月")
    print(f"  {'价格路径':<16} {'一次性收益':>8} {'定投收益':>8} {'定投平均成本':>10} {'期末价格':>8}")
    for name, px in paths(a.months).items():
        lump = total / px[0] * px[-1]
        shares = sum(a.monthly / px[k] for k in range(a.months))
        dca = shares * px[-1]
        print(f"  {name:<16} {(lump / total - 1) * 100:>+9.1f}% {(dca / total - 1) * 100:>+9.1f}% {total / shares:>12.3f} {px[-1]:>10.2f}")


if __name__ == "__main__":
    main()
