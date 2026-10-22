#!/usr/bin/env python3
"""行为损耗模拟：同一只基金，纪律型与追涨杀跌型投资者的结果差多少（第 14 章配套工具，仅用标准库）

用法：
    python3 tools/behavior_gap.py
    python3 tools/behavior_gap.py --stop 10 --chase 20

价格路径（人为构造的形状，不是任何真实基金）：48 个月，
    前 18 个月从 1.0 加速涨到 1.8，随后 12 个月匀速跌到 1.0，最后 18 个月先慢后快涨到 1.5。

两位投资者：
    纪律型：每月固定投入 1,000，从不卖出。
    追涨杀跌型：每月也投 1,000；近 3 个月涨幅超过 --chase% 时额外加投 3,000（「越涨越敢买」）；
              账户浮亏（相对这一轮的投入成本）超过 --stop% 时全部卖出（「受不了了」），
              卖出后暂停投资，直到近 3 个月涨幅再次超过 --chase% 才重新开始。

输出：
    基金本身的收益（时间加权，买入并持有 1 元的结果）
    每位投资者的投入、期末资产、资金加权年化收益（IRR，按每笔资金进出的时间计算）
"""
import argparse


def path():
    px = []
    for k in range(19):
        px.append(1.0 + 0.8 * (k / 18) ** 2)
    for k in range(1, 13):
        px.append(1.8 - 0.8 * k / 12)
    for k in range(1, 19):
        px.append(1.0 + 0.5 * (k / 18) ** 2)
    return px


def irr(flows):
    lo, hi = -0.99, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        npv = sum(cf / (1 + mid) ** t for t, cf in flows)
        lo, hi = (mid, hi) if npv > 0 else (lo, mid)
    return (1 + (lo + hi) / 2) ** 12 - 1


def run(px, chaser, a):
    shares, flows, invested, active, cost = 0.0, [], 0.0, True, 0.0
    log = []
    for t in range(len(px) - 1):
        p = px[t]
        trail = p / px[t - 3] - 1 if t >= 3 else 0
        if chaser:
            value = shares * p
            if shares > 0 and value < cost * (1 - a.stop / 100):
                flows.append((t, value))
                log.append(f"第 {t} 月 净值 {p:.2f} 浮亏 {1 - value / cost:.0%}，全部卖出 {value:,.0f}")
                shares, cost, active = 0.0, 0.0, False
                continue
            if not active and trail > a.chase / 100:
                active = True
                log.append(f"第 {t} 月 净值 {p:.2f} 近 3 月涨 {trail:.0%}，重新开始买入")
        if not active:
            continue
        amt = 1000.0
        if chaser and trail > a.chase / 100:
            amt += 3000
        shares += amt / p
        invested += amt
        cost += amt
        flows.append((t, -amt))
    final = shares * px[-1]
    flows.append((len(px) - 1, final))
    cash_out = sum(cf for t, cf in flows[:-1] if cf > 0)
    return invested, final + cash_out, irr(flows), log


def main() -> None:
    p = argparse.ArgumentParser(description="行为损耗模拟")
    p.add_argument("--stop", type=float, default=15, help="浮亏多少就清仓（%%）")
    p.add_argument("--chase", type=float, default=15, help="近 3 月涨幅超过多少就加仓（%%）")
    a = p.parse_args()
    px = path()
    years = (len(px) - 1) / 12
    print(f"基金净值 1.00 → 最高 1.80 → 最低 1.00 → 期末 {px[-1]:.2f}；"
          f"买入并持有的年化收益 {(px[-1] / px[0]) ** (1 / years) - 1:.1%}")
    print(f"  {'投资者':<8} {'累计投入':>8} {'期末资产(含已卖出)':>16} {'资金加权年化':>10}")
    for name, ch in (("纪律型", False), ("追涨杀跌型", True)):
        inv, fin, r, log = run(px, ch, a)
        print(f"  {name:<8} {inv:>10,.0f} {fin:>18,.0f} {r * 100:>+12.1f}%")
        for line in log:
            print(f"      {line}")


if __name__ == "__main__":
    main()
