#!/usr/bin/env python3
"""个人资产负债表 + 现金流量表 + 财务体检（第 2 章配套工具，仅用标准库）

用法：
    # 看小林的报表
    python3 tools/personal_statements.py cases/xiaolin/ch02-statements.json

    # 生成一份空白模板，填上你自己的数字
    python3 tools/personal_statements.py --template > my-statements.json
    python3 tools/personal_statements.py my-statements.json

数据文件说明（JSON）：
    assets       资产清单，category 只能是：流动 / 投资 / 受限 / 自用
                 value 填「今天卖掉能拿到的钱」，可选 cost 填当初花了多少
    liabilities  负债清单，value 填「今天一次性还清要多少钱」，monthly_payment 填每月还款额
    income       每月收入（税后）
    expenses     每月生活支出（不含还债，还债从 liabilities 自动汇总）
    reconcile    可选，用于「现金对账」：months 个月前的现金余额 cash_start；
                 cash_end 不填则默认取当前「流动」类资产合计

体检指标的参考值来自国内理财规划教材与媒体中常见的经验值，不同来源数值略有出入，
只用于发现问题，不是硬标准。
"""
import argparse
import json
import sys

CATEGORIES = ["流动", "投资", "受限", "自用"]

TEMPLATE = {
    "name": "我",
    "date": "YYYY-MM",
    "assets": [
        {"name": "银行活期 + 货币基金", "category": "流动", "value": 0},
        {"name": "基金 / 股票（按今天市值）", "category": "投资", "value": 0, "cost": 0},
        {"name": "住房公积金余额", "category": "受限", "value": 0},
        {"name": "手机电脑等（按二手价）", "category": "自用", "value": 0, "cost": 0},
    ],
    "liabilities": [
        {"name": "信用卡本期未还账单", "value": 0, "monthly_payment": 0},
        {"name": "分期 / 消费贷剩余本金", "value": 0, "monthly_payment": 0},
    ],
    "income": [{"name": "税后工资", "value": 0}],
    "expenses": [
        {"name": "房租 / 房贷以外的住房", "value": 0},
        {"name": "餐饮", "value": 0},
        {"name": "交通", "value": 0},
        {"name": "其他", "value": 0},
    ],
    "reconcile": {"months": 3, "cash_start": 0},
}


def money(x: float) -> str:
    return f"{x:,.0f}"


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def section(title: str) -> None:
    print()
    print(f"== {title} ==")


def main() -> None:
    p = argparse.ArgumentParser(description="个人财务报表与体检")
    p.add_argument("file", nargs="?", help="数据文件（JSON）")
    p.add_argument("--template", action="store_true", help="打印空白模板")
    a = p.parse_args()

    if a.template:
        print(json.dumps(TEMPLATE, ensure_ascii=False, indent=2))
        return
    if not a.file:
        p.error("请提供数据文件，或用 --template 生成模板")

    with open(a.file, encoding="utf-8") as f:
        d = json.load(f)

    assets = d.get("assets", [])
    liabs = d.get("liabilities", [])
    for x in assets:
        if x.get("category") not in CATEGORIES:
            sys.exit(f"资产「{x.get('name')}」的 category 必须是 {CATEGORIES} 之一")

    by_cat = {c: sum(x["value"] for x in assets if x["category"] == c) for c in CATEGORIES}
    total_assets = sum(by_cat.values())
    total_liabs = sum(x["value"] for x in liabs)
    net_worth = total_assets - total_liabs
    usable_assets = by_cat["流动"] + by_cat["投资"]
    usable_net_worth = usable_assets - total_liabs

    income = sum(x["value"] for x in d.get("income", []))
    living = sum(x["value"] for x in d.get("expenses", []))
    debt_pay = sum(x.get("monthly_payment", 0) for x in liabs)
    outflow = living + debt_pay
    surplus = income - outflow

    print(f"{d.get('name', '')} 的个人财务报表（{d.get('date', '')}）")

    section("一、资产负债表（存量：此刻我有什么、欠什么）")
    for c in CATEGORIES:
        items = [x for x in assets if x["category"] == c]
        if not items:
            continue
        print(f"  [{c}资产] 小计 {money(by_cat[c])}")
        for x in items:
            note = ""
            if "cost" in x and x["cost"]:
                diff = x["value"] - x["cost"]
                note = f"   （成本 {money(x['cost'])}，{'浮盈' if diff >= 0 else '缩水'} {money(abs(diff))}）"
            print(f"      {x['name']:<20} {money(x['value']):>10}{note}")
    print(f"  资产合计 {money(total_assets):>27}")
    print("  [负债]")
    for x in liabs:
        print(f"      {x['name']:<20} {money(x['value']):>10}")
    print(f"  负债合计 {money(total_liabs):>27}")
    print(f"  账面净资产 = 资产 - 负债 {money(net_worth):>14}")
    print(f"  可动用净资产（剔除受限、自用） {money(usable_net_worth):>8}")

    section("二、现金流量表（流量：每个月钱怎么进、怎么出）")
    for x in d.get("income", []):
        print(f"  收入  {x['name']:<20} {money(x['value']):>10}")
    for x in d.get("expenses", []):
        print(f"  支出  {x['name']:<20} {money(x['value']):>10}")
    for x in liabs:
        if x.get("monthly_payment"):
            print(f"  还债  {x['name']:<20} {money(x['monthly_payment']):>10}")
    print(f"  收入合计 {money(income):>27}")
    print(f"  生活支出 {money(living):>27}")
    print(f"  还债支出 {money(debt_pay):>27}")
    print(f"  月结余（按记录） {money(surplus):>19}")

    real_outflow = outflow
    rc = d.get("reconcile")
    if rc and rc.get("cash_start"):
        section("三、现金对账（两张表互相验证）")
        months = rc["months"]
        cash_start = rc["cash_start"]
        cash_end = rc.get("cash_end", by_cat["流动"])
        expected = cash_start + surplus * months
        gap = expected - cash_end
        print(f"  {months} 个月前现金 {money(cash_start):>22}")
        print(f"  + 按记录的结余 {money(surplus)} x {months} 个月 = {money(surplus * months):>9}")
        print(f"  = 理论上现在应有 {money(expected):>18}")
        print(f"  实际现在只有 {money(cash_end):>22}")
        print(f"  对不上的钱 {money(gap):>24}   即每月约 {money(gap / months)} 没有记录")
        real_outflow = outflow + gap / months
        print(f"  修正后月支出 {money(real_outflow):>22}")
        print(f"  修正后月结余 {money(income - real_outflow):>22}")

    section("四、财务体检（参考值为常见经验值，不同来源略有出入）")
    rows = []
    real_surplus = income - real_outflow
    rows.append(("结余比率", "月结余 / 月税后收入", real_surplus / income if income else 0,
                 "30% 以上较健康", lambda v: v >= 0.3, pct))
    rows.append(("流动性比率", "流动资产 / 月支出", by_cat["流动"] / real_outflow if real_outflow else 0,
                 "3 到 6 个月", lambda v: 3 <= v <= 6, lambda v: f"{v:.1f} 个月"))
    rows.append(("资产负债率（账面）", "总负债 / 总资产", total_liabs / total_assets if total_assets else 0,
                 "低于 50%", lambda v: v < 0.5, pct))
    rows.append(("资产负债率（可动用）", "总负债 / (流动+投资)", total_liabs / usable_assets if usable_assets else 0,
                 "低于 50%", lambda v: v < 0.5, pct))
    rows.append(("负债收入比率", "月还债 / 月税后收入", debt_pay / income if income else 0,
                 "低于 35% 到 40%", lambda v: v < 0.35, pct))
    rows.append(("投资与净资产比率", "投资资产 / 账面净资产", by_cat["投资"] / net_worth if net_worth > 0 else 0,
                 "长期目标 50% 左右", lambda v: v >= 0.5, pct))
    for name, formula, v, ref, ok, fmt in rows:
        flag = "达标" if ok(v) else "关注"
        print(f"  {name:<12} {fmt(v):>10}   [{flag}]  参考：{ref}；公式：{formula}")


if __name__ == "__main__":
    main()
