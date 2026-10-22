#!/usr/bin/env python3
"""A 股交易成本与股票回报拆解（第 9 章配套工具，仅用标准库）

用法：
    # 一买一卖的成本（佣金费率按你和券商约定的填，单位 %）
    python3 tools/stock_cost.py cost --amount 10000 --commission 0.025

    # 交易频率对长期收益的拖累：每年换手 N 次
    python3 tools/stock_cost.py drag --commission 0.025 --turnover 1 4 12 50

    # 股票长期回报拆解：股息率 + 盈利增长 + 估值变化
    python3 tools/stock_cost.py decompose --dividend 2.5 --growth 5 --pe-start 15 --pe-end 12 --years 10

费用口径（2026-10 检索，均以券商实际收费为准）：
    印花税 0.05%，仅卖出方缴纳；过户费 0.001%，买卖双向；
    佣金不超过成交金额 0.3%，双向收取，常见单笔最低 5 元（各券商公示表）。
"""
import argparse

STAMP = 0.0005
TRANSFER = 0.00001


def one_side(amount: float, commission: float, sell: bool) -> float:
    fee = max(5.0, amount * commission) + amount * TRANSFER
    if sell:
        fee += amount * STAMP
    return fee


def cmd_cost(a) -> None:
    c = a.commission / 100
    buy = one_side(a.amount, c, False)
    sell = one_side(a.amount, c, True)
    total = buy + sell
    print(f"成交金额 {a.amount:,.0f}，佣金费率 {a.commission}%（最低 5 元）")
    print(f"  买入成本 {buy:,.2f}  卖出成本 {sell:,.2f}（含印花税 {a.amount * STAMP:,.2f}）")
    print(f"  一买一卖合计 {total:,.2f}，占成交额 {total / a.amount * 100:.3f}%")
    print(f"  也就是说，股价至少要涨 {total / a.amount * 100:.3f}% 才能打平成本")


def cmd_drag(a) -> None:
    c = a.commission / 100
    rt = c * 2 + TRANSFER * 2 + STAMP
    print(f"佣金 {a.commission}%（按大额成交、不触发 5 元最低计），一买一卖成本约 {rt * 100:.3f}%")
    print(f"  {'年换手次数':>8} {'每年成本':>8} {'10 年累计拖累':>12}")
    for n in a.turnover:
        yearly = rt * n
        ten = 1 - (1 - yearly) ** 10 if yearly < 1 else 1
        print(f"  {n:>10} {yearly * 100:>9.2f}% {ten * 100:>13.1f}%")


def cmd_decompose(a) -> None:
    val = (a.pe_end / a.pe_start) ** (1 / a.years) - 1
    total = (1 + a.growth / 100) * (1 + val) - 1 + a.dividend / 100
    print(f"假设：股息率 {a.dividend}%，每股盈利年增长 {a.growth}%，市盈率 {a.years} 年间从 {a.pe_start} 变到 {a.pe_end}")
    print(f"  估值变化每年贡献 {val * 100:+.2f}%")
    print(f"  年化总回报 ≈ 股息 {a.dividend}% + 盈利增长 {a.growth}% + 估值变化 {val * 100:+.2f}%（含交叉项）≈ {total * 100:.2f}%")


def main() -> None:
    p = argparse.ArgumentParser(description="A 股交易成本与回报拆解")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("cost")
    s.add_argument("--amount", type=float, required=True)
    s.add_argument("--commission", type=float, default=0.025, help="佣金费率（%%）")
    s = sub.add_parser("drag")
    s.add_argument("--commission", type=float, default=0.025)
    s.add_argument("--turnover", type=float, nargs="+", required=True)
    s = sub.add_parser("decompose")
    s.add_argument("--dividend", type=float, required=True, help="股息率（%%）")
    s.add_argument("--growth", type=float, required=True, help="每股盈利年增长（%%）")
    s.add_argument("--pe-start", type=float, required=True)
    s.add_argument("--pe-end", type=float, required=True)
    s.add_argument("--years", type=int, required=True)
    a = p.parse_args()
    {"cost": cmd_cost, "drag": cmd_drag, "decompose": cmd_decompose}[a.cmd](a)


if __name__ == "__main__":
    main()
