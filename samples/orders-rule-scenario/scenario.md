# 场景描述

订单表 orders 需要保证成交价格和订单状态的合法性。

# 业务规则

- deal_price 必须大于 0。
- 状态为“已完成”时，completed_at 不能为空。
- 状态为“已取消”时，completed_at 必须为空。
- buyer_id 不能等于 seller_id。
- status 只能取：待付款、待发货、待收货、已完成、已取消。
