# 理财从小白到精通

> 一门以「老师连载」方式写成的个人理财课程。从「钱到底是什么」讲起，一路讲到资产配置、读财报、估值和人生财务规划。
> 每章一个 md 文件，按顺序读即可；每章末尾有自测题，答不出来就回到对应的积木块重读。

## 怎么用这门课

- **按顺序读**。前五章是「守住钱」，后面才是「让钱生钱」。跳过地基直接学选股，是新手亏钱最常见的路径。
- **边学边动手**。`tools/` 下有可运行的 Python 小工具（只用标准库），每章会告诉你跑哪个。
- **跟着小林走**。`cases/xiaolin/` 是贯穿全课的虚构案例：一个 28 岁、财务状况一团乱的年轻人，我们每章帮他解决一个问题。
- **本课只讲方法，不荐具体产品**。书中出现的任何基金类型、指数、数字都是教学示例，不构成投资建议。

## 课程表

### 第一阶段 小白：先搞懂钱，守住钱

| 章 | 标题 | 文件 | 状态 |
|---|---|---|---|
| 01 | 理财到底是什么：钱的四个去处、复利与通胀 | [01-what-is-financial-planning.md](chapters/01-what-is-financial-planning.md) | 已发布 |
| 02 | 给自己做一张财务报表：资产负债表与现金流量表 | [02-personal-financial-statements.md](chapters/02-personal-financial-statements.md) | 已发布 |
| 03 | 记账与预算：让每一块钱都有去处 | [03-budgeting.md](chapters/03-budgeting.md) | 已发布 |
| 04 | 安全垫：应急金、负债管理与个人信用 | [04-emergency-fund-debt.md](chapters/04-emergency-fund-debt.md) | 已发布 |
| 05 | 保险：用小钱转移大风险 | [05-insurance.md](chapters/05-insurance.md) | 已发布 |

### 第二阶段 入门：认识每一种工具

| 章 | 标题 | 文件 | 状态 |
|---|---|---|---|
| 06 | 风险、收益、流动性：理财的不可能三角 | `06-risk-return-liquidity.md` | 待发布 |
| 07 | 现金管理：存款、货币基金、国债逆回购 | `07-cash-management.md` | 待发布 |
| 08 | 债券与固收：利率、久期与信用 | `08-bonds.md` | 待发布 |
| 09 | 股票是什么：股权、交易所与 A 股规则 | `09-stocks-basics.md` | 待发布 |
| 10 | 基金全景：主动基金、指数基金、ETF、FOF | `10-funds.md` | 待发布 |
| 11 | 指数基金与定投：普通人的最优解之一 | `11-index-investing.md` | 待发布 |

### 第三阶段 进阶：把工具组合成体系

| 章 | 标题 | 文件 | 状态 |
|---|---|---|---|
| 12 | 资产配置：决定长期结果的那件事 | `12-asset-allocation.md` | 待发布 |
| 13 | 再平衡与投资纪律 | `13-rebalancing.md` | 待发布 |
| 14 | 投资心理学：你最大的敌人是自己 | `14-behavioral-finance.md` | 待发布 |
| 15 | 税费与账户：个税、公积金、个人养老金、交易成本 | `15-tax-accounts.md` | 待发布 |
| 16 | 更多资产：黄金、REITs、海外资产 | `16-alternative-assets.md` | 待发布 |

### 第四阶段 精通：看懂公司、看懂周期

| 章 | 标题 | 文件 | 状态 |
|---|---|---|---|
| 17 | 读懂财报：利润表、资产负债表、现金流量表 | `17-reading-financial-reports.md` | 待发布 |
| 18 | 估值：PE、PB、股息率与 DCF | `18-valuation.md` | 待发布 |
| 19 | 宏观与周期：利率、通胀与经济周期 | `19-macro-cycles.md` | 待发布 |
| 20 | 风险管理：波动、回撤与压力测试 | `20-risk-management.md` | 待发布 |
| 21 | 人生财务规划：买房、教育、养老 | `21-life-planning.md` | 待发布 |
| 22 | 毕业设计：防骗指南与你的终身理财系统 | `22-capstone.md` | 待发布 |
| 附录 | 术语表 + 公式速查 + 书单 | `appendix.md` | 待发布 |

## 学习路线图

```mermaid
flowchart LR
    A["小白 01-05<br/>守住钱"] --> B["入门 06-11<br/>认识工具"]
    B --> C["进阶 12-16<br/>组合成体系"]
    C --> D["精通 17-22<br/>看懂公司与周期"]
```

## 目录结构

```text
.
├── README.md                 课程总纲（本文件）
├── chapters/                 正文，每章一个文件
│   ├── 01-what-is-financial-planning.md
│   ├── 02-personal-financial-statements.md
│   ├── 03-budgeting.md
│   ├── 04-emergency-fund-debt.md
│   └── 05-insurance.md
├── cases/
│   └── xiaolin/              贯穿案例：小林的财务改造
│       ├── README.md
│       ├── ch02-statements.json   第 2 章：小林的报表数据
│       ├── ch03-budget.json       第 3 章：小林的新预算
│       └── ch03-transactions.csv  第 3 章：小林 10 月流水
└── tools/                    配套 Python 小工具（仅标准库）
    ├── compound_interest.py  复利 / 定投 / 通胀计算器
    ├── personal_statements.py 个人资产负债表 / 现金流量表 / 财务体检
    ├── budget.py             预算 vs 实际 + 50/30/20 检查
    ├── debt_apr.py           分期真实年化（IRR）+ 应急金测算
    └── insurance_needs.py    重疾 / 寿险保额与保费预算测算
```

## 免责声明

本课程内容仅用于个人学习，不构成任何投资建议。市场有风险，投资需谨慎。任何投资决策应结合个人风险承受能力、资金状况和投资目标独立判断，必要时咨询持牌专业机构。过往表现不预示未来收益。
