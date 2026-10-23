#!/usr/bin/env python3
"""财报体检：从几个关键数字看危险信号（第 17 章配套工具，仅用标准库）

用法：
    python3 tools/financial_health.py examples/healthy.json
    python3 tools/financial_health.py examples/risky.json

数据文件（JSON，单位：元，同一口径、同一期）：
    revenue        营业收入
    revenue_prev   上期营业收入
    gross_profit   毛利
    net_profit     净利润（归母）
    ocf            经营活动产生的现金流量净额
    receivables    应收账款
    receivables_prev 上期应收账款
    inventory      存货
    inventory_prev 上期存货
    total_assets   总资产
    total_liab     总负债
    interest_debt  有息负债（短期借款+长期借款+应付债券等）
    cash           货币资金
    goodwill       商誉
    equity         所有者权益
"""
import json
import sys


def pct(x):
    return f"{x * 100:.1f}%"


def growth(cur, prev):
    return (cur / prev - 1) if prev else float("nan")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    g = lambda k: d.get(k, 0)

    rev, rev_p = g("revenue"), g("revenue_prev")
    gp, np_, ocf = g("gross_profit"), g("net_profit"), g("ocf")
    ar, ar_p = g("receivables"), g("receivables_prev")
    inv, inv_p = g("inventory"), g("inventory_prev")
    ta, tl = g("total_assets"), g("total_liab")
    idebt, cash = g("interest_debt"), g("cash")
    gw, eq = g("goodwill"), g("equity")

    print(f"{d.get('name', '公司')} 财报体检")
    print("\n一、盈利能力")
    print(f"  毛利率        {pct(gp / rev)}")
    print(f"  净利率        {pct(np_ / rev)}")
    print(f"  净资产收益率  {pct(np_ / eq) if eq else '-'}")
    print(f"  收入增速      {pct(growth(rev, rev_p)) if rev_p else '-'}")

    print("\n二、利润的质量")
    ratio = ocf / np_ if np_ else float("nan")
    print(f"  经营现金流 / 净利润  {ratio:.2f}" if np_ else "  经营现金流 / 净利润  -")
    print(f"    {'偏低：利润没有变成现金，重点查应收账款和存货' if np_ and ratio < 0.8 else '正常'}")

    print("\n三、异常信号")
    flags = []
    if rev_p and ar_p:
        gr, ga = growth(rev, rev_p), growth(ar, ar_p)
        if ga - gr > 0.10:
            flags.append(f"应收账款增速 {pct(ga)} 明显高于收入增速 {pct(gr)}（可能放宽信用换收入）")
    if rev_p and inv_p:
        gi = growth(inv, inv_p)
        if gi - growth(rev, rev_p) > 0.20:
            flags.append(f"存货增速 {pct(gi)} 远高于收入增速（可能滞销积压）")
    if ta and tl / ta > 0.7:
        flags.append(f"资产负债率 {pct(tl / ta)} 偏高（超过 70%）")
    if cash and idebt > cash:
        flags.append(f"有息负债 {idebt:,.0f} 高于货币资金 {cash:,.0f}（偿债压力）")
    if cash and idebt and cash / ta > 0.2 and idebt / ta > 0.2:
        flags.append("存贷双高：账上钱不少却大量借款，需要解释")
    if eq and gw / eq > 0.3:
        flags.append(f"商誉占净资产 {pct(gw / eq)}（超过 30%，减值风险）")
    if np_ and ocf < 0:
        flags.append("净利润为正但经营现金流为负（最需要警惕的组合）")
    print("\n".join(f"  - {f}" for f in flags) if flags else "  未触发常见异常规则")

    print("\n注：只是规则式的初筛，不构成任何判断；真实分析要结合行业、口径和多年数据。")


if __name__ == "__main__":
    main()
