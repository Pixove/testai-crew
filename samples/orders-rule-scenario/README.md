# orders 规则测试样本

该样本演示“场景驱动”流程在 orders 表上的效果。

## 内容

- `sample.db`：已应用 orders 规则触发器的样本数据库
- `scenario.md`：用户场景描述
- `scenario_rules.json`：业务规则
- `business_scenarios.json`：业务场景
- `test_cases.json`：测试用例
- `test_data.json`：测试数据
- `generated_test_suite.json`：生成的测试套件
- `pytest_result.json`：pytest 实际执行结果
- `coverage_report.json`：覆盖率报告
- `review_report.md`：质量审查报告
- `automated_tests/`：可执行 pytest

## 规则

- `deal_price` 必须大于 0
- 状态为“已完成”时，`completed_at` 不能为空
- 状态为“已取消”时，`completed_at` 必须为空
- `buyer_id` 不能等于 `seller_id`
- `status` 只能取：`待付款`、`待发货`、`待收货`、`已完成`、`已取消`

## 预期失败

`status` 枚举规则**故意没有在样本数据库中实现**。运行样本测试会出现 5 条
预期的 `规则未落地: status=...` 失败，用来演示“规则只存在于场景描述中，
但数据库没有强制”的情况。

要让这些测试通过，需要给 `status` 添加 `CHECK` 约束或触发器，只允许五个
枚举值。

## 确定性质量评分

该样本的确定性质量评分为 **97/100**：

```text
规则覆盖率        40/40   5 条规则都有场景、用例和数据
场景分类覆盖率    25/25   normal / boundary / exception 全覆盖
测试数据完整率    20/20   29 条用例都有测试数据
pytest 通过率     12/15   24 passed / 5 failed
```

5 条失败来自被测数据库未实现 `status` 枚举规则，属于被测系统缺陷，
不是测试套件本身的质量问题。

## 运行样本测试

```powershell
python -m pytest samples\orders-rule-scenario\automated_tests -v
```

样本 conftest 直接读取同目录下的 `sample.db`，不需要额外配置数据库。
