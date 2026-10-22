#!/usr/bin/env python3
"""再平衡模拟与计算（第 13 章配套工具，仅用标准库）

用法：
    # 比较三种策略：不再平衡 / 每年再平衡 / 偏离超过阈值再平衡（股 40 / 债 60，10 年）
    python3 tools/rebalance.py sim --stock 40 --years 10 --band 5

    # 计算：把一个桶调回目标比例，「卖出调整」和「只用新增资金调整」各要多少钱、多久
    python3 tools/rebalance.py plan --stock-value 10500 --bond-value 0 --target 40 --monthly 500

说明：
    - sim 用假设参数按月模拟（股票类收益 8% 波动 20%，债券类收益 3% 波动 4%，相关系数 0），
      固定随机种子 11。参数是教学用的量级，不代表任何产品。
    - plan 假设调整期间价格不变，只算资金搬运，用来估计「靠新钱调回来」要多久。
"""
import argparse
import math
import random


def run(strategy, a, rng_seed):
    rng = random.Random(rng_seed)
    ms, ss = 0.08 / 12, 0.20 / math.sqrt(12)
    mb, sb = 0.03 / 12, 0.04 / math.sqrt(12)
    target = a.stock / 100
    res = []
    for _ in range(a.n):
        s, b = target, 1 - target
        peak, dd, trades, max_w = 1.0, 0.0, 0, target
        for m in range(1, a.years * 12 + 1):
            s *= 1 + ms + ss * rng.gauss(0, 1)
            b *= 1 + mb + sb * rng.gauss(0, 1)
            v = s + b
            w = s / v
            max_w = max(max_w, w)
            do = (strategy == "每年再平衡" and m % 12 == 0) or \
                 (strategy == "阈值再平衡" and abs(w - target) * 100 > a.band)
            if do:
                s, b = v * target, v * (1 - target)
                trades += 1
            peak = max(peak, v)
            dd = max(dd, 1 - v / peak)
        res.append((s + b, dd, s / (s + b), trades, max_w))
    n = len(res)
    finals = sorted(r[0] for r in res)
    return (sum(r[0] for r in res) / n, finals[int(n * 0.05)], sum(r[1] for r in res) / n,
            sum(r[2] for r in res) / n, sum(r[3] for r in res) / n, sum(r[4] for r in res) / n)


def cmd_sim(a) -> None:
    print(f"目标 股 {a.stock}% / 债 {100 - a.stock}%，{a.years} 年，模拟 {a.n} 次（每种策略用同一组随机路径）")
    print(f"  {'策略':<10} {'平均终值':>8} {'最差5%终值':>10} {'平均最大回撤':>10} {'期末股票占比':>10} {'途中最高股票占比':>14} {'平均操作次数':>10}")
    for st in ("不再平衡", "每年再平衡", "阈值再平衡"):
        mean, p05, dd, w, tr, mw = run(st, a, 11)
        label = st if st != "阈值再平衡" else f"阈值±{a.band:g}"
        print(f"  {label:<10} {mean:>10.2f} {p05:>11.2f} {dd * 100:>12.1f}% {w * 100:>12.1f}% {mw * 100:>15.1f}% {tr:>12.1f}")


def cmd_plan(a) -> None:
    S, B, t = a.stock_value, a.bond_value, a.target / 100
    total = S + B
    print(f"当前：股 {S:,.0f} / 债 {B:,.0f}，股票占比 {S / total:.1%}，目标 {a.target:g}%")
    sell = S - total * t
    if sell > 0:
        print(f"  方案 A 卖出调整：卖出股票 {sell:,.0f}，买入债券，立即达到目标")
        need_bond = S * (1 - t) / t - B
        months = need_bond / a.monthly if a.monthly else float("inf")
        print(f"  方案 B 只用新钱：每月 {a.monthly:,.0f} 全部买债，需要再投入债券 {need_bond:,.0f}，约 {months:.1f} 个月")
    else:
        print("  股票占比不高于目标，无需卖出股票")


def main() -> None:
    p = argparse.ArgumentParser(description="再平衡模拟与计算")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sim")
    s.add_argument("--stock", type=float, default=40)
    s.add_argument("--years", type=int, default=10)
    s.add_argument("--band", type=float, default=5, help="阈值（百分点）")
    s.add_argument("--n", type=int, default=2000)
    s = sub.add_parser("plan")
    s.add_argument("--stock-value", type=float, required=True)
    s.add_argument("--bond-value", type=float, required=True)
    s.add_argument("--target", type=float, required=True, help="目标股票占比（%%）")
    s.add_argument("--monthly", type=float, default=0, help="每月新增资金")
    a = p.parse_args()
    cmd_sim(a) if a.cmd == "sim" else cmd_plan(a)


if __name__ == "__main__":
    main()
