#!/usr/bin/env python3
"""复利 / 定投 / 通胀计算器（第 1 章配套工具，仅用标准库）

用法示例：
    # 1 万元一次性投入，年化 5%，放 30 年
    python3 tools/compound_interest.py --principal 10000 --rate 5 --years 30

    # 每月定投 2000 元，年化 5%，30 年，同时看 3% 通胀下的实际购买力
    python3 tools/compound_interest.py --monthly 2000 --rate 5 --years 30 --inflation 3

    # 72 法则：按某个收益率，钱翻倍要多少年
    python3 tools/compound_interest.py --double 6

说明：
    - 收益率、通胀率都按「年化百分比」输入，例如 5 表示 5%。
    - 定投按月复利计算（月利率 = 年化 / 12），每月月末投入。
    - 所有收益率都是假设值，用来理解复利机制，不代表任何产品的真实或预期收益。
"""
import argparse
import math


def future_value(principal: float, monthly: float, annual_rate: float, years: int):
    """逐年返回 (年份, 累计投入, 期末资产)。"""
    m = annual_rate / 12
    balance = principal
    invested = principal
    rows = []
    for year in range(1, years + 1):
        for _ in range(12):
            balance = balance * (1 + m) + monthly
            invested += monthly
        rows.append((year, invested, balance))
    return rows


def main() -> None:
    p = argparse.ArgumentParser(description="复利 / 定投 / 通胀计算器")
    p.add_argument("--principal", type=float, default=0, help="一次性投入本金（元）")
    p.add_argument("--monthly", type=float, default=0, help="每月定投金额（元）")
    p.add_argument("--rate", type=float, default=5, help="假设年化收益率（%%）")
    p.add_argument("--years", type=int, default=30, help="投资年限")
    p.add_argument("--inflation", type=float, default=0, help="假设年通胀率（%%），用于换算实际购买力")
    p.add_argument("--double", type=float, help="只算翻倍时间：输入年化收益率（%%）")
    p.add_argument("--every", type=int, default=5, help="每隔几年打印一行")
    a = p.parse_args()

    if a.double:
        r = a.double / 100
        exact = math.log(2) / math.log(1 + r)
        print(f"年化 {a.double}%：72 法则估算 {72 / a.double:.1f} 年，精确值 {exact:.1f} 年")
        return

    if a.principal <= 0 and a.monthly <= 0:
        p.error("至少提供 --principal 或 --monthly 之一")

    rows = future_value(a.principal, a.monthly, a.rate / 100, a.years)
    header = f"{'年份':>4} {'累计投入':>12} {'期末资产':>12} {'其中收益':>12}"
    if a.inflation:
        header += f" {'折合今天的钱':>12}"
    print(f"假设：本金 {a.principal:,.0f} 元，每月 {a.monthly:,.0f} 元，年化 {a.rate}%，通胀 {a.inflation}%")
    print(header)
    for year, invested, balance in rows:
        if year % a.every and year != a.years:
            continue
        line = f"{year:>6} {invested:>14,.0f} {balance:>14,.0f} {balance - invested:>14,.0f}"
        if a.inflation:
            real = balance / (1 + a.inflation / 100) ** year
            line += f" {real:>16,.0f}"
        print(line)


if __name__ == "__main__":
    main()
