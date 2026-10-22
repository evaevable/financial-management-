#!/usr/bin/env python3
"""现金管理计算器（第 7 章配套工具，仅用标准库）

用法：
    # 比较一笔钱放在不同现金工具里一年的利息（利率为你自己查到的数，单位 %）
    python3 tools/cash_tools.py compare --amount 46000 --rates 活期=0.05 货币基金=1.0 一年定期=0.95

    # 定期提前支取的损失：一年定期，存了 10 个月要取
    python3 tools/cash_tools.py early --amount 20000 --rate 0.95 --demand 0.05 --months 10 --term 12

    # 应急金分层：总额 + 各层占比
    python3 tools/cash_tools.py ladder --amount 46000 --layers 银行活期=0.2 货币基金=0.8

说明：
    - 利率必须自己去银行 App、基金 App 查最新值；本工具不内置任何利率。
    - 存款按单利、按实际天数折算；货币基金收益每天浮动，这里用你输入的年化近似计算。
    - 定期存款提前支取，按《储蓄管理条例》等规定通常按支取日活期利率计息，以银行规则为准。
"""
import argparse


def parse_pairs(items):
    out = []
    for it in items:
        k, v = it.split("=", 1)
        out.append((k, float(v)))
    return out


def cmd_compare(a) -> None:
    print(f"本金 {a.amount:,.0f} 元，存放 1 年的利息（按你输入的年化利率）")
    for name, r in parse_pairs(a.rates):
        print(f"  {name:<10} 年化 {r:>5.2f}%   利息约 {a.amount * r / 100:>8,.0f} 元")


def cmd_early(a) -> None:
    full = a.amount * a.rate / 100 * a.term / 12
    early = a.amount * a.demand / 100 * a.months / 12
    print(f"本金 {a.amount:,.0f}，{a.term} 个月定期，年化 {a.rate}%")
    print(f"  存满到期的利息         {full:>8,.2f} 元")
    print(f"  第 {a.months} 个月提前支取（按活期 {a.demand}%）利息 {early:>8,.2f} 元")
    print(f"  如果放活期 {a.months} 个月，利息也是 {early:,.2f} 元：提前支取等于白存定期")


def cmd_ladder(a) -> None:
    layers = parse_pairs(a.layers)
    total = sum(p for _, p in layers)
    if abs(total - 1) > 1e-6:
        raise SystemExit(f"各层占比之和应为 1，当前为 {total}")
    print(f"应急金 {a.amount:,.0f} 元分层：")
    for name, p in layers:
        print(f"  {name:<10} {p:>5.0%}   {a.amount * p:>8,.0f} 元")


def main() -> None:
    p = argparse.ArgumentParser(description="现金管理计算器")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compare")
    c.add_argument("--amount", type=float, required=True)
    c.add_argument("--rates", nargs="+", required=True, help="名称=年化利率%%")
    e = sub.add_parser("early")
    e.add_argument("--amount", type=float, required=True)
    e.add_argument("--rate", type=float, required=True, help="定期年化%%")
    e.add_argument("--demand", type=float, required=True, help="活期年化%%")
    e.add_argument("--months", type=int, required=True, help="实际存了几个月")
    e.add_argument("--term", type=int, default=12, help="定期期限（月）")
    l = sub.add_parser("ladder")
    l.add_argument("--amount", type=float, required=True)
    l.add_argument("--layers", nargs="+", required=True, help="名称=占比（小数）")
    a = p.parse_args()
    {"compare": cmd_compare, "early": cmd_early, "ladder": cmd_ladder}[a.cmd](a)


if __name__ == "__main__":
    main()
