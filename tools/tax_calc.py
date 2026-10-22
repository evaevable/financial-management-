#!/usr/bin/env python3
"""个税计算器：综合所得、年终奖两种计税方式、个人养老金节税（第 15 章配套工具，仅用标准库）

用法：
    # 月薪（税前）15000，三险一金个人部分每月 3075，专项附加扣除每月 4500，年终奖 30000
    python3 tools/tax_calc.py --salary 15000 --insurance 3075 --special 4500 --bonus 30000

    # 再加上每年存 12000 个人养老金
    python3 tools/tax_calc.py --salary 15000 --insurance 3075 --special 4500 --pension 12000

    # 年终奖「临界点」演示
    python3 tools/tax_calc.py --bonus-edge

口径（2026-10 检索核实）：
    - 居民个人综合所得按年计税，基本减除费用 60,000 元/年，税率表为 3%-45% 七级超额累进。
    - 全年一次性奖金单独计税政策延续至 2027-12-31：奖金 / 12 查月度税率表。
    - 个人养老金：每年 12,000 元限额内据实扣除，领取时按 3% 单独计税
      （财政部 税务总局公告 2024 年第 21 号）。
    - 本工具只做年度测算，不处理劳务报酬、稿酬、经营所得等其他所得。
"""
import argparse

ANNUAL = [(36000, 0.03, 0), (144000, 0.10, 2520), (300000, 0.20, 16920), (420000, 0.25, 31920),
          (660000, 0.30, 52920), (960000, 0.35, 85920), (float("inf"), 0.45, 181920)]
MONTHLY = [(3000, 0.03, 0), (12000, 0.10, 210), (25000, 0.20, 1410), (35000, 0.25, 2660),
           (55000, 0.30, 4410), (80000, 0.35, 7160), (float("inf"), 0.45, 15160)]


def tax(amount, table):
    if amount <= 0:
        return 0.0, 0.0
    for top, rate, quick in table:
        if amount <= top:
            return amount * rate - quick, rate
    raise ValueError


def bonus_tax(bonus):
    _, rate = tax(bonus / 12, MONTHLY)
    for top, r, quick in MONTHLY:
        if r == rate:
            return bonus * rate - quick
    return 0.0


def main() -> None:
    p = argparse.ArgumentParser(description="个税计算器")
    p.add_argument("--salary", type=float, default=0, help="月薪（税前）")
    p.add_argument("--insurance", type=float, default=0, help="每月三险一金个人缴纳部分")
    p.add_argument("--special", type=float, default=0, help="每月专项附加扣除合计")
    p.add_argument("--bonus", type=float, default=0, help="全年一次性奖金")
    p.add_argument("--pension", type=float, default=0, help="每年个人养老金缴存（上限 12000）")
    p.add_argument("--bonus-edge", action="store_true", help="演示年终奖临界点")
    a = p.parse_args()

    if a.bonus_edge:
        print("年终奖单独计税的临界点（奖金 / 12 跨档时，整笔奖金适用更高税率）")
        for b in (36000, 36001, 38566.67, 144000, 144001, 160500):
            t = bonus_tax(b)
            print(f"  奖金 {b:>11,.2f}  税 {t:>10,.2f}  到手 {b - t:>11,.2f}")
        return

    pension = min(a.pension, 12000)
    base = a.salary * 12 - 60000 - a.insurance * 12 - a.special * 12 - pension
    t_sep_salary, rate = tax(base, ANNUAL)
    t_sep = t_sep_salary + bonus_tax(a.bonus)
    t_comb, rate_comb = tax(base + a.bonus, ANNUAL)
    print(f"年工资 {a.salary * 12:,.0f}，三险一金 {a.insurance * 12:,.0f}，专项附加扣除 {a.special * 12:,.0f}，"
          f"个人养老金 {pension:,.0f}，年终奖 {a.bonus:,.0f}")
    print(f"  工资部分应纳税所得额 {max(base, 0):,.0f}，适用最高税率 {rate:.0%}")
    if a.bonus:
        print(f"  方式一 年终奖单独计税：合计个税 {t_sep:,.2f}")
        print(f"  方式二 并入综合所得：  合计个税 {t_comb:,.2f}（最高税率 {rate_comb:.0%}）")
        print(f"  选{'单独计税' if t_sep <= t_comb else '并入综合所得'}更省 {abs(t_sep - t_comb):,.2f}")
    else:
        print(f"  全年个税 {t_sep_salary:,.2f}")
    if pension:
        no_p, _ = tax(base + pension, ANNUAL)
        save = no_p - t_sep_salary
        print(f"  个人养老金当年少交个税 {save:,.2f}；将来领取时按 3% 缴税 {pension * 0.03:,.2f}；"
              f"净节税约 {save - pension * 0.03:,.2f}（不计投资收益，且资金锁定到退休）")


if __name__ == "__main__":
    main()
