# 场景描述

商品表新增字段 discount_rate。

# 业务规则

- price 为 0 时，discount_rate 必须为 0。
- price 大于 0 时，discount_rate 可以为 0，也可以大于 0。
- discount_rate 不能为负数。
