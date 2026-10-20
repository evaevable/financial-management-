#!/usr/bin/env python3
"""预算 vs 实际 + 50/30/20 检查（第 3 章配套工具，仅用标准库）

用法：
    python3 tools/budget.py cases/xiaolin/ch03-budget.json cases/xiaolin/ch03-transactions.csv

budget.json：income 为月税后收入；categories 每项含 name、kind、budget。
    kind 只能是：需要 / 想要 / 还债 / 储蓄
    「储蓄」类不需要出现在流水里，实际储蓄 = 收入 - 实际总支出。
transactions.csv：表头 date,category,amount,note，category 必须和 budget 里的 name 一致。

50/30/20 口径（Elizabeth Warren 与 Amelia Warren Tyagi《All Your Worth》，2005）：
    需要 50%（含每月最低还款），想要 30%，储蓄与额外还债 20%。本工具把「还债」计入「需要」。
"""
import csv
import json
import sys
from collections import defaultdict

KINDS = ["需要", "想要", "还债", "储蓄"]


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    budget = json.load(open(sys.argv[1], encoding="utf-8"))
    income = budget["income"]
    cats = {c["name"]: c for c in budget["categories"]}
    for c in cats.values():
        if c["kind"] not in KINDS:
            sys.exit(f"分类「{c['name']}」的 kind 必须是 {KINDS} 之一")

    actual = defaultdict(float)
    rows = []
    with open(sys.argv[2], encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r["category"] not in cats:
                sys.exit(f"流水分类「{r['category']}」不在预算里，请先在预算中添加")
            amt = float(r["amount"])
            actual[r["category"]] += amt
            rows.append((amt, r["date"], r["category"], r["note"]))

    spent = sum(actual.values())
    print(f"月税后收入 {income:,.0f}，流水 {len(rows)} 笔，实际总支出 {spent:,.0f}\n")
    print(f"{'分类':<10}{'类型':<6}{'预算':>8}{'实际':>8}{'差额':>8}  状态")
    for name, c in cats.items():
        if c["kind"] == "储蓄":
            act = income - spent
            diff = act - c["budget"]
            status = "达标" if diff >= 0 else "未达标"
        else:
            act = actual.get(name, 0)
            diff = c["budget"] - act
            status = "超支" if diff < 0 else "正常"
        print(f"{name:<10}{c['kind']:<6}{c['budget']:>8,.0f}{act:>8,.0f}{diff:>8,.0f}  {status}")

    def split(get):
        need = sum(get(n) for n, c in cats.items() if c["kind"] in ("需要", "还债"))
        want = sum(get(n) for n, c in cats.items() if c["kind"] == "想要")
        return need, want, income - need - want

    print("\n50/30/20 检查（目标：需要 50% / 想要 30% / 储蓄 20%）")
    for label, get in (("预算", lambda n: cats[n]["budget"]), ("实际", lambda n: actual.get(n, 0))):
        need, want, save = split(get)
        print(f"  {label}：需要 {need / income:.1%}  想要 {want / income:.1%}  储蓄 {save / income:.1%}")

    print("\n「想要」类最大的 5 笔支出（最值得复盘）：")
    wants = sorted((r for r in rows if cats[r[2]]["kind"] == "想要"), reverse=True)[:5]
    for amt, date, cat, note in wants:
        print(f"  {date}  {cat:<8}{amt:>8,.0f}  {note}")


if __name__ == "__main__":
    main()
