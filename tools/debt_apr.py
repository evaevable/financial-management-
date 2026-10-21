#!/usr/bin/env python3
"""分期真实年化 + 应急金测算（第 4 章配套工具，仅用标准库）

用法：
    # 分期：本金 12000，分 12 期，每期手续费率 0.6%（按初始本金收取）
    python3 tools/debt_apr.py apr --principal 12000 --periods 12 --fee 0.6

    # 应急金：每月必要支出 7600，现有流动资金 30000，每月可存 2300
    python3 tools/debt_apr.py emergency --essential 7600 --cash 30000 --saving 2300

说明：
    - 信用卡分期常见的收费方式是「每期手续费 = 初始本金 x 每期费率」，但本金逐月在减少，
      所以真实年化（按内部收益率 IRR 计算）远高于「每期费率 x 12」。
    - 名义年化 = 月 IRR x 12；实际年化 = (1 + 月 IRR)^12 - 1。
"""
import argparse


def monthly_irr(principal: float, payment: float, periods: int) -> float:
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        pv = sum(payment / (1 + mid) ** k for k in range(1, periods + 1))
        lo, hi = (mid, hi) if pv > principal else (lo, mid)
    return (lo + hi) / 2


def cmd_apr(a) -> None:
    fee = a.principal * a.fee / 100
    payment = a.principal / a.periods + fee
    r = monthly_irr(a.principal, payment, a.periods)
    print(f"本金 {a.principal:,.0f}，{a.periods} 期，每期手续费率 {a.fee}%")
    print(f"  每期还款 {payment:,.2f}（本金 {a.principal / a.periods:,.2f} + 手续费 {fee:,.2f}）")
    print(f"  手续费合计 {fee * a.periods:,.2f}")
    print(f"  表面费率 每期费率 x 12 = {a.fee * 12:.2f}%")
    print(f"  名义年化（IRR x 12）= {r * 12 * 100:.2f}%")
    print(f"  实际年化（复利）     = {((1 + r) ** 12 - 1) * 100:.2f}%")
    n = a.periods
    print(f"  速算 每期费率 x 24n/(n+1) = {a.fee * 24 * n / (n + 1):.2f}%")


def cmd_emergency(a) -> None:
    print(f"每月必要支出 {a.essential:,.0f}，现有流动资金 {a.cash:,.0f}，每月可存 {a.saving:,.0f}")
    print(f"  当前可撑 {a.cash / a.essential:.1f} 个月")
    for m in (3, 6):
        target = a.essential * m
        gap = max(0.0, target - a.cash)
        months = gap / a.saving if a.saving else float("inf")
        print(f"  {m} 个月目标 {target:,.0f}，缺口 {gap:,.0f}，按每月存 {a.saving:,.0f} 约需 {months:.1f} 个月")


def main() -> None:
    p = argparse.ArgumentParser(description="分期真实年化 + 应急金测算")
    sub = p.add_subparsers(dest="cmd", required=True)
    s1 = sub.add_parser("apr")
    s1.add_argument("--principal", type=float, required=True)
    s1.add_argument("--periods", type=int, required=True)
    s1.add_argument("--fee", type=float, required=True, help="每期手续费率（%%）")
    s2 = sub.add_parser("emergency")
    s2.add_argument("--essential", type=float, required=True, help="每月必要支出")
    s2.add_argument("--cash", type=float, required=True, help="现有流动资金")
    s2.add_argument("--saving", type=float, default=0, help="每月可存入")
    a = p.parse_args()
    cmd_apr(a) if a.cmd == "apr" else cmd_emergency(a)


if __name__ == "__main__":
    main()
