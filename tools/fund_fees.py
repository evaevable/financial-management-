#!/usr/bin/env python3
"""基金费用拖累计算器（第 10 章配套工具，仅用标准库）

用法：
    # 默认比较三种费率结构，10 万元、假设毛收益 7%、持有 20 年
    python3 tools/fund_fees.py

    # 自定义
    python3 tools/fund_fees.py --amount 100000 --gross 7 --years 20 \
        --fund 主动基金:1.2:0.2:0.8 --fund 场外指数:0.5:0.1:0.3 --fund 宽基ETF:0.15:0.05:0

说明：
    --fund 格式为 名称:管理费%:托管费%:一次性申购费%（均为年化或一次性比例）
    - 管理费、托管费每天从基金资产中计提，你在净值里看不到单独扣款，但它一直在发生。
    - 默认费率是教学假设：主动基金取改革后的上限（管理费 1.2%、托管费 0.2%，
      申购费上限 0.8%，见证监会公告〔2025〕22 号）；指数类为常见量级，具体以基金合同为准。
    - 毛收益为假设值；另有交易佣金、销售服务费等未计入。
"""
import argparse

DEFAULT = ["主动基金:1.2:0.2:0.8", "场外指数:0.5:0.1:0.3", "宽基ETF:0.15:0.05:0"]


def main() -> None:
    p = argparse.ArgumentParser(description="基金费用拖累计算器")
    p.add_argument("--amount", type=float, default=100000)
    p.add_argument("--gross", type=float, default=7, help="扣费前假设年化收益（%%）")
    p.add_argument("--years", type=int, default=20)
    p.add_argument("--fund", action="append", help="名称:管理费:托管费:申购费")
    a = p.parse_args()
    funds = a.fund or DEFAULT

    no_fee = a.amount * (1 + a.gross / 100) ** a.years
    print(f"本金 {a.amount:,.0f}，假设扣费前年化 {a.gross}%，持有 {a.years} 年；不计任何费用时终值 {no_fee:,.0f}")
    print(f"  {'名称':<8} {'年费合计':>8} {'终值':>12} {'被费用吃掉':>12} {'占比':>7}")
    for f in funds:
        name, mgmt, cust, buy = f.split(":")
        yearly = (float(mgmt) + float(cust)) / 100
        start = a.amount * (1 - float(buy) / 100)
        final = start * (1 + a.gross / 100 - yearly) ** a.years
        lost = no_fee - final
        print(f"  {name:<8} {yearly * 100:>7.2f}% {final:>13,.0f} {lost:>13,.0f} {lost / no_fee * 100:>6.1f}%")


if __name__ == "__main__":
    main()
