#!/usr/bin/env python3
"""保险需求测算（第 5 章配套工具，仅用标准库）

用法：
    python3 tools/insurance_needs.py --income 144000 --debt 20000 --liquid 30000 \
        --dependents-spend 0 --dependents-years 0 --recovery-years 3

估算逻辑（行业常用的经验方法，不是精算结果）：
    重疾险保额  = 年收入 x 康复期年数（覆盖治疗和康复期间的收入损失；
                  医疗费主要交给医疗险，所以这里不重复计算）
    寿险保额    = 负债 + 被供养人年支出 x 供养年数 - 现有流动资产（不低于 0）
    年保费预算  = 年收入的 5% 到 10%（经验区间，不同来源说法不一）
"""
import argparse


def main() -> None:
    p = argparse.ArgumentParser(description="保险需求测算")
    p.add_argument("--income", type=float, required=True, help="税后年收入")
    p.add_argument("--debt", type=float, default=0, help="负债总额")
    p.add_argument("--liquid", type=float, default=0, help="现有流动资产")
    p.add_argument("--dependents-spend", type=float, default=0, help="需要你供养的人每年支出")
    p.add_argument("--dependents-years", type=float, default=0, help="还需供养多少年")
    p.add_argument("--recovery-years", type=float, default=3, help="重疾康复期按几年收入算（常见 3-5 年）")
    a = p.parse_args()

    ci = a.income * a.recovery_years
    life = max(0.0, a.debt + a.dependents_spend * a.dependents_years - a.liquid)
    print(f"税后年收入 {a.income:,.0f}")
    print(f"  重疾险建议保额  {ci:,.0f}  （年收入 x {a.recovery_years:g} 年康复期）")
    if life:
        print(f"  寿险建议保额    {life:,.0f}  （负债 + 供养需求 - 流动资产）")
    else:
        print("  寿险建议保额    0  （负债可被现有资产覆盖，且没有人靠你的收入生活，暂不急需）")
    print("  医疗险          百万医疗险，保额通常数百万，覆盖住院大额自费")
    print("  意外险          保额可参考 年收入 x 3 到 5，并含意外医疗")
    print(f"  年保费预算      {a.income * 0.05:,.0f} 到 {a.income * 0.10:,.0f}  （年收入 5% 到 10%）")


if __name__ == "__main__":
    main()
