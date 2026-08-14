# QA Review Report

共 5 条业务规则（RULE-orders-001~005）、21 个业务场景、29 个测试用例（TC-orders-001~029）与 29 条测试数据（TD-orders-001~029），pytest 套件 29 个测试函数与用例一一对应。数据库 orders 表字段（order_id, product_id, buyer_id, seller_id, deal_price, status, created_at, completed_at）与测试字段完全一致，且无任何 CHECK/触发器级约束，规则校验完全依赖应用层——因此所有‘应拒绝’用例在规则未落地时会以“规则未落地”报错，属预期设计。各规则单规则取值类（allowed/forbidden/boundary/NULL）覆盖完备，RULE-005 枚举覆盖最全（5 个合法值 + 5 种非法形态），并含全规则合法组合用例 TC-029；主要缺口为跨规则交叉/多违例叠加组合、UPDATE 状态流转组合，以及规则本身未定义（R004 NULL、R002 空串/非法格式）时采用的宽松双通道断言。

## Coverage Matrix

| Rule | Scenarios | Test Cases | Data Records | Covered |
|------|-----------|------------|--------------|---------|
| RULE-orders-001 | 5 | 6 | 6 | True |
| RULE-orders-002 | 4 | 6 | 6 | True |
| RULE-orders-003 | 3 | 5 | 5 | True |
| RULE-orders-004 | 4 | 5 | 5 | True |
| RULE-orders-005 | 5 | 11 | 11 | True |

## Missing Combinations
- 多规则同时违例叠加组合缺失：仅 TC-029 覆盖全部规则均合法的正向组合，缺少如 status='已完成'+deal_price=0、status='已取消'+completed_at 非空+buyer_id=seller_id 等多条规则同时失败的用例
- RULE-orders-001 × RULE-orders-002 交叉矩阵未覆盖：status='已完成' 时 deal_price 取 0/负数/NULL 与 completed_at 非空/NULL 的配对组合未测试
- RULE-orders-004 × RULE-orders-005 交叉矩阵未覆盖：buyer_id=seller_id、buyer/seller 一方或双方 NULL 与五枚举值（尤其已完成、已取消）边界的组合未测试
- RULE-orders-004 的 NULL 边界（单方 NULL、双方 NULL）仅有宽松双通道断言，未在业务确认后形成确定性预期与唯一结果
- RULE-orders-002 的 completed_at 空字符串与非法格式采用双通道断言，未形成确定预期；completed_at 早于 created_at 的时序语义组合未覆盖
- UPDATE 状态流转组合缺失：待付款→已完成强制补 completed_at、待发货→已取消清空 completed_at 等状态迁移路径未测试（当前仅覆盖 INSERT）
- 存量数据审计缺失：未验证 orders 表既有 400 行数据是否违反五条规则（存量违规数据检测）

## Quality Score: 84/100

## Recommendations
- 补充多规则同时违例的叠加组合用例（至少覆盖两条规则同时失败），验证校验逻辑叠加时的拒绝行为
- 构建 R001×R002、R004×R005 的交叉组合矩阵，将 status 边界值（已完成、已取消、NULL）与 deal_price、buyer/seller_id 边界配对测试
- 与业务确认 RULE-orders-004 的 NULL 语义（NULL 是否视为同一人），将宽松断言改为确定性断言并明确唯一预期结果
- 与业务确认 completed_at 空字符串、非法格式及早于 created_at 的处理策略，补充格式与时序校验规则及对应确定性用例
- 新增 UPDATE 状态流转测试，覆盖状态迁移时 completed_at 的强制填充/清空约束
- 新增存量数据规则审计用例，对 orders 现有 400 行数据执行五条规则的符合性检查
- 保持现有单规则 allowed/forbidden/boundary/NULL 取值类覆盖作为基线，无需缩减，仅在上层补充交叉与流转用例

## Conclusion
测试套件对五条规则的覆盖度较高且自洽：21 个场景、29 个用例、29 条数据与 29 个 pytest 函数一一对应，字段落地核对与 FK 前置处理（_ensure_product）到位，单规则的 allowed/forbidden/boundary/NULL 四类取值基本完备，RULE-005 枚举覆盖尤为完整，且具备全规则合法的正向组合用例（TC-029）。主要不足集中在组合层面：缺少多规则同时违例与跨规则交叉组合、缺少 UPDATE 状态流转测试，且对规则未定义的 NULL/空字符串/非法格式行为采用了宽松双通道断言，无法给出确定性判定。综合评定 84/100，按上述 7 项建议补齐后可提升至 95 分以上。