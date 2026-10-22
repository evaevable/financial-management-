#!/usr/bin/env python3
"""债券计算器（第 8 章配套工具，仅用标准库）

用法：
    # 一只面值 100、票面利率 2.5%、剩余 10 年、每年付息一次的债券，市场收益率 2.5% 时的价格与久期
    python3 tools/bond_calc.py price --coupon 2.5 --years 10 --ytm 2.5

    # 利率变动对价格的影响：精确重算 vs 久期估算
    python3 tools/bond_calc.py shock --coupon 2.5 --years 10 --ytm 2.5 --shifts -1 -0.5 0.5 1

    # 比较不同期限的利率敏感度
    python3 tools/bond_calc.py compare --coupon 2.5 --ytm 2.5 --years 1 3 5 10 30

    # 信用风险：违约概率与回收率对「真实期望收益」的影响
    python3 tools/bond_calc.py credit --ytm 6 --pd 3 --recovery 40

说明：
    - 所有利率、收益率都是假设值，用来理解机制。
    - 久期估算：价格变动 ≈ -修正久期 x 利率变动；利率变动越大，误差越大（凸性）。
    - 信用期望收益是一年期的粗略近似：≈ 收益率 - 违约概率 x (1 - 回收率)。
"""
import argparse


def cashflows(coupon: float, years: int, face: float = 100.0):
    return [(t, face * coupon + (face if t == years else 0)) for t in range(1, years + 1)]


def price(coupon: float, years: int, ytm: float) -> float:
    return sum(cf / (1 + ytm) ** t for t, cf in cashflows(coupon, years))


def durations(coupon: float, years: int, ytm: float):
    p = price(coupon, years, ytm)
    mac = sum(t * cf / (1 + ytm) ** t for t, cf in cashflows(coupon, years)) / p
    return mac, mac / (1 + ytm)


def cmd_price(a) -> None:
    c, y = a.coupon / 100, a.ytm / 100
    p = price(c, a.years, y)
    mac, mod = durations(c, a.years, y)
    print(f"面值 100，票面利率 {a.coupon}%，剩余 {a.years} 年，市场收益率 {a.ytm}%")
    print(f"  价格           {p:.2f}")
    print(f"  麦考利久期     {mac:.2f} 年")
    print(f"  修正久期       {mod:.2f}  （利率每变动 1 个百分点，价格约反向变动 {mod:.2f}%）")


def cmd_shock(a) -> None:
    c, y = a.coupon / 100, a.ytm / 100
    p0 = price(c, a.years, y)
    _, mod = durations(c, a.years, y)
    print(f"票面 {a.coupon}%，剩余 {a.years} 年，当前收益率 {a.ytm}%，价格 {p0:.2f}，修正久期 {mod:.2f}")
    print(f"  {'利率变动':>8} {'新价格':>8} {'精确涨跌':>8} {'久期估算':>8}")
    for s in a.shifts:
        p1 = price(c, a.years, y + s / 100)
        print(f"  {s:>+8.2f}% {p1:>9.2f} {(p1 / p0 - 1) * 100:>+9.2f}% {-mod * s:>+9.2f}%")


def cmd_compare(a) -> None:
    c, y = a.coupon / 100, a.ytm / 100
    print(f"票面 {a.coupon}%、收益率 {a.ytm}% 时，不同剩余期限的利率敏感度")
    print(f"  {'剩余年限':>6} {'修正久期':>8} {'利率上升 1 个百分点':>14}")
    for n in a.years:
        p0 = price(c, n, y)
        p1 = price(c, n, y + 0.01)
        print(f"  {n:>8} {durations(c, n, y)[1]:>10.2f} {(p1 / p0 - 1) * 100:>+16.2f}%")


def cmd_credit(a) -> None:
    exp = a.ytm - a.pd * (1 - a.recovery / 100)
    print(f"收益率 {a.ytm}%，假设年违约概率 {a.pd}%，违约后回收 {a.recovery}%")
    print(f"  一年期粗略期望收益 ≈ {a.ytm} - {a.pd} x {1 - a.recovery / 100:.2f} = {exp:.2f}%")
    print(f"  但若真违约：这笔钱当年约亏 {100 - a.recovery:.0f}%（不是平均的小损失，而是集中的大损失）")


def main() -> None:
    p = argparse.ArgumentParser(description="债券计算器")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("price", "shock"):
        s = sub.add_parser(name)
        s.add_argument("--coupon", type=float, required=True)
        s.add_argument("--years", type=int, required=True)
        s.add_argument("--ytm", type=float, required=True)
        if name == "shock":
            s.add_argument("--shifts", type=float, nargs="+", required=True, help="利率变动（百分点）")
    s = sub.add_parser("compare")
    s.add_argument("--coupon", type=float, required=True)
    s.add_argument("--ytm", type=float, required=True)
    s.add_argument("--years", type=int, nargs="+", required=True)
    s = sub.add_parser("credit")
    s.add_argument("--ytm", type=float, required=True)
    s.add_argument("--pd", type=float, required=True, help="年违约概率（%%）")
    s.add_argument("--recovery", type=float, required=True, help="违约回收率（%%）")
    a = p.parse_args()
    {"price": cmd_price, "shock": cmd_shock, "compare": cmd_compare, "credit": cmd_credit}[a.cmd](a)


if __name__ == "__main__":
    main()
