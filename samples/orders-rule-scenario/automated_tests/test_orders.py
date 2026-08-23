'''Automated pytest suite for the orders table.

Generated from test_cases.json. Each test maps to one test case id
(e.g. test_tc_orders_001 -> TC-orders-001) and runs the recorded insert
operation against a temporary copy of the source database.

Rules under test:
  RULE-orders-001: deal_price must be greater than 0.
  RULE-orders-002: when status = '\u5df2\u5b8c\u6210', completed_at must not be NULL.
  RULE-orders-003: when status = '\u5df2\u53d6\u6d88', completed_at must be NULL.
  RULE-orders-004: buyer_id must not equal seller_id.
  RULE-orders-005: status must be one of the five enum values.
'''

import sqlite3

import pytest

ORDERS_FIELDS = [
    'order_id',
    'product_id',
    'buyer_id',
    'seller_id',
    'deal_price',
    'status',
    'created_at',
    'completed_at',
]


def _assert_fields_present(db_conn, table, fields):
    '''Fail with \u5b57\u6bb5\u672a\u843d\u5730 when a required field is missing in the table.'''
    columns = {row['name'] for row in db_conn.execute(f'PRAGMA table_info({table})')}
    missing = [field for field in fields if field not in columns]
    if missing:
        pytest.fail(f'\u5b57\u6bb5\u672a\u843d\u5730: \u8868 {table} \u7f3a\u5c11\u5b57\u6bb5 {missing}')


def _ensure_product(db_conn):
    '''Satisfy the FK precondition: product_id=1 must exist in products.'''
    exists = db_conn.execute('SELECT 1 FROM products WHERE product_id = 1').fetchone()
    if exists is not None:
        return
    seller_id = db_conn.execute('SELECT MIN(student_id) AS sid FROM students').fetchone()['sid']
    db_conn.execute(
        'INSERT INTO products (product_id, seller_id, title, price, status) '
        'VALUES (?, ?, ?, ?, ?)',
        (1, seller_id, 'precondition-product', 1.0, '\u5728\u552e'),
    )
    db_conn.commit()


def _clean_order(db_conn, order_id):
    '''Satisfy the precondition: the target order_id must not pre-exist.'''
    db_conn.execute('DELETE FROM orders WHERE order_id = ?', (order_id,))
    db_conn.commit()


def _try_insert(db_conn, table, fields):
    '''Run the insert operation. Return None on success, otherwise the exception.'''
    columns = ', '.join(fields.keys())
    placeholders = ', '.join('?' * len(fields))
    sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
    try:
        db_conn.execute(sql, tuple(fields.values()))
        db_conn.commit()
        return None
    except sqlite3.Error as exc:
        db_conn.rollback()
        return exc


def test_tc_orders_001(db_conn):
    '''TC-orders-001: \u6210\u4ea4\u4ef7\u683c\u4e3a\u6b63\u6570\u65f6\u6821\u9a8c\u901a\u8fc7.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1001)
    fields = {
        'order_id': 1001,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 68.13,
        'status': '\u5f85\u53d1\u8d27',
        'created_at': '2024-06-01 10:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is not None:
        pytest.fail(f'\u89c4\u5219\u672a\u843d\u5730: \u5408\u6cd5\u8ba2\u5355 deal_price=68.13>0 \u63d2\u5165\u88ab\u62d2\u7edd: {err}')
    row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1001,)).fetchone()
    assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u6210\u529f\u540e\u672a\u67e5\u8be2\u5230 order_id=1001 \u7684\u8bb0\u5f55'
    assert row['deal_price'] == pytest.approx(68.13)


def test_tc_orders_002(db_conn):
    '''TC-orders-002: \u6210\u4ea4\u4ef7\u683c\u7b49\u4e8e 0 \u65f6\u6821\u9a8c\u5931\u8d25.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1002)
    fields = {
        'order_id': 1002,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 0,
        'status': '\u5f85\u4ed8\u6b3e',
        'created_at': '2024-06-02 09:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is None:
        pytest.fail('\u89c4\u5219\u672a\u843d\u5730: deal_price=0 \u8fdd\u53cd\u201c\u5fc5\u987b\u5927\u4e8e 0\u201d\uff0c\u4f46\u6570\u636e\u5e93\u63a5\u53d7\u4e86\u63d2\u5165')


def test_tc_orders_003(db_conn):
    '''TC-orders-003: \u6210\u4ea4\u4ef7\u683c\u4e3a\u6781\u5c0f\u6b63\u6570\u65f6\u6821\u9a8c\u901a\u8fc7.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1003)
    fields = {
        'order_id': 1003,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 0.01,
        'status': '\u5f85\u53d1\u8d27',
        'created_at': '2024-06-03 09:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is not None:
        pytest.fail(f'\u89c4\u5219\u672a\u843d\u5730: \u5408\u6cd5\u8ba2\u5355 deal_price=0.01>0 \u63d2\u5165\u88ab\u62d2\u7edd: {err}')
    row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1003,)).fetchone()
    assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u6210\u529f\u540e\u672a\u67e5\u8be2\u5230 order_id=1003 \u7684\u8bb0\u5f55'
    assert row['deal_price'] == pytest.approx(0.01)


def test_tc_orders_004(db_conn):
    '''TC-orders-004: \u6210\u4ea4\u4ef7\u683c\u4e3a NULL \u65f6\u6821\u9a8c\u5931\u8d25.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1004)
    fields = {
        'order_id': 1004,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': None,
        'status': '\u5f85\u53d1\u8d27',
        'created_at': '2024-06-04 09:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is None:
        pytest.fail('\u89c4\u5219\u672a\u843d\u5730: deal_price=NULL \u65e0\u6cd5\u6ee1\u8db3\u201c\u5fc5\u987b\u5927\u4e8e 0\u201d\uff0c\u4f46\u6570\u636e\u5e93\u63a5\u53d7\u4e86\u63d2\u5165')


def test_tc_orders_005(db_conn):
    '''TC-orders-005: \u6210\u4ea4\u4ef7\u683c\u4e3a\u8d1f\u6570\u65f6\u6821\u9a8c\u5931\u8d25.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1005)
    fields = {
        'order_id': 1005,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': -15.96,
        'status': '\u5f85\u4ed8\u6b3e',
        'created_at': '2024-06-05 09:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is None:
        pytest.fail('\u89c4\u5219\u672a\u843d\u5730: deal_price=-15.96 \u8fdd\u53cd\u201c\u5fc5\u987b\u5927\u4e8e 0\u201d\uff0c\u4f46\u6570\u636e\u5e93\u63a5\u53d7\u4e86\u63d2\u5165')


def test_tc_orders_006(db_conn):
    '''TC-orders-006: \u5df2\u5b8c\u6210\u8ba2\u5355\u5b8c\u6210\u65f6\u95f4\u975e\u7a7a\u65f6\u6821\u9a8c\u901a\u8fc7.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1006)
    fields = {
        'order_id': 1006,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 88.0,
        'status': '\u5df2\u5b8c\u6210',
        'created_at': '2024-06-10 09:00:00',
        'completed_at': '2024-06-15 10:30:00',
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is not None:
        pytest.fail(f'\u89c4\u5219\u672a\u843d\u5730: status=\u201c\u5df2\u5b8c\u6210\u201d\u4e14 completed_at \u975e\u7a7a\u65f6\u63d2\u5165\u88ab\u62d2\u7edd: {err}')
    row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1006,)).fetchone()
    assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u6210\u529f\u540e\u672a\u67e5\u8be2\u5230 order_id=1006 \u7684\u8bb0\u5f55'
    assert row['completed_at'] == '2024-06-15 10:30:00'


def test_tc_orders_007(db_conn):
    '''TC-orders-007: \u5df2\u5b8c\u6210\u8ba2\u5355\u5b8c\u6210\u65f6\u95f4\u4e3a NULL \u65f6\u6821\u9a8c\u5931\u8d25.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1007)
    fields = {
        'order_id': 1007,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 88.0,
        'status': '\u5df2\u5b8c\u6210',
        'created_at': '2024-06-10 09:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is None:
        pytest.fail('\u89c4\u5219\u672a\u843d\u5730: status=\u201c\u5df2\u5b8c\u6210\u201d\u65f6 completed_at=NULL \u8fdd\u53cd\u201c\u4e0d\u80fd\u4e3a\u7a7a\u201d\uff0c\u4f46\u6570\u636e\u5e93\u63a5\u53d7\u4e86\u63d2\u5165')


def test_tc_orders_008(db_conn):
    '''TC-orders-008: \u5df2\u5b8c\u6210\u8ba2\u5355\u5b8c\u6210\u65f6\u95f4\u4ec5\u542b\u7a7a\u5b57\u7b26\u4e32\u65f6\u6821\u9a8c\u7ed3\u679c\u5f85\u786e\u8ba4.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1008)
    fields = {
        'order_id': 1008,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 88.0,
        'status': '\u5df2\u5b8c\u6210',
        'created_at': '2024-06-10 09:00:00',
        'completed_at': '',
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is None:
        row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1008,)).fetchone()
        assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u88ab\u63a5\u53d7\u4f46\u672a\u67e5\u8be2\u5230 order_id=1008 \u7684\u8bb0\u5f55'
        assert row['completed_at'] == ''
    # \u88ab\u62d2\u7edd\u4e5f\u540c\u6837\u53ef\u63a5\u53d7\uff1a\u8be5\u8fb9\u754c\u884c\u4e3a\u672a\u5b9a\u4e49\uff0c\u9700\u4e1a\u52a1\u786e\u8ba4


def test_tc_orders_009(db_conn):
    '''TC-orders-009: \u5df2\u5b8c\u6210\u8ba2\u5355\u5b8c\u6210\u65f6\u95f4\u4e3a\u975e\u6cd5\u683c\u5f0f\u65f6\u8bed\u4e49\u5f02\u5e38.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1009)
    fields = {
        'order_id': 1009,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 88.0,
        'status': '\u5df2\u5b8c\u6210',
        'created_at': '2024-06-10 09:00:00',
        'completed_at': 'not-a-date',
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is None:
        row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1009,)).fetchone()
        assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u88ab\u63a5\u53d7\u4f46\u672a\u67e5\u8be2\u5230 order_id=1009 \u7684\u8bb0\u5f55'
        assert row['completed_at'] == 'not-a-date'
    # \u88ab\u62d2\u7edd\u4e5f\u540c\u6837\u53ef\u63a5\u53d7\uff1a\u8be5\u7ec4\u5408\u672a\u8986\u76d6\uff0c\u9700\u4e1a\u52a1\u8865\u5145\u683c\u5f0f\u6821\u9a8c


def test_tc_orders_010(db_conn):
    '''TC-orders-010: \u975e\u5df2\u5b8c\u6210\u8ba2\u5355\u5b8c\u6210\u65f6\u95f4\u4e3a NULL \u65f6\u89c4\u5219\u4e0d\u9002\u7528\u6821\u9a8c\u901a\u8fc7.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1010)
    fields = {
        'order_id': 1010,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 50.0,
        'status': '\u5f85\u4ed8\u6b3e',
        'created_at': '2024-06-11 09:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is not None:
        pytest.fail(f'\u89c4\u5219\u672a\u843d\u5730: status=\u201c\u5f85\u4ed8\u6b3e\u201d\u4e0d\u9002\u7528 RULE-orders-002\uff0c\u4f46\u63d2\u5165\u88ab\u62d2\u7edd: {err}')
    row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1010,)).fetchone()
    assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u6210\u529f\u540e\u672a\u67e5\u8be2\u5230 order_id=1010 \u7684\u8bb0\u5f55'


def test_tc_orders_011(db_conn):
    '''TC-orders-011: \u5df2\u53d6\u6d88\u8ba2\u5355\u5b8c\u6210\u65f6\u95f4\u4e3a NULL \u65f6\u6821\u9a8c\u901a\u8fc7.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1011)
    fields = {
        'order_id': 1011,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 30.0,
        'status': '\u5df2\u53d6\u6d88',
        'created_at': '2024-06-12 09:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is not None:
        pytest.fail(f'\u89c4\u5219\u672a\u843d\u5730: status=\u201c\u5df2\u53d6\u6d88\u201d\u4e14 completed_at=NULL \u65f6\u63d2\u5165\u88ab\u62d2\u7edd: {err}')
    row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1011,)).fetchone()
    assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u6210\u529f\u540e\u672a\u67e5\u8be2\u5230 order_id=1011 \u7684\u8bb0\u5f55'


def test_tc_orders_012(db_conn):
    '''TC-orders-012: \u5df2\u53d6\u6d88\u8ba2\u5355\u5b8c\u6210\u65f6\u95f4\u4e3a\u7a7a\u5b57\u7b26\u4e32\u65f6\u6821\u9a8c\u5931\u8d25.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1012)
    fields = {
        'order_id': 1012,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 30.0,
        'status': '\u5df2\u53d6\u6d88',
        'created_at': '2024-06-12 09:00:00',
        'completed_at': '',
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is None:
        pytest.fail('\u89c4\u5219\u672a\u843d\u5730: status=\u201c\u5df2\u53d6\u6d88\u201d\u65f6 completed_at=\'\' \u5c5e\u4e8e\u975e NULL \u503c\uff0c\u4f46\u6570\u636e\u5e93\u63a5\u53d7\u4e86\u63d2\u5165')


def test_tc_orders_013(db_conn):
    '''TC-orders-013: \u5df2\u53d6\u6d88\u8ba2\u5355\u5b8c\u6210\u65f6\u95f4\u975e\u7a7a\u65f6\u6821\u9a8c\u5931\u8d25.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1013)
    fields = {
        'order_id': 1013,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 30.0,
        'status': '\u5df2\u53d6\u6d88',
        'created_at': '2024-06-12 09:00:00',
        'completed_at': '2024-05-20 08:00:00',
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is None:
        pytest.fail('\u89c4\u5219\u672a\u843d\u5730: status=\u201c\u5df2\u53d6\u6d88\u201d\u65f6 completed_at \u975e\u7a7a\uff0c\u4f46\u6570\u636e\u5e93\u63a5\u53d7\u4e86\u63d2\u5165')


def test_tc_orders_014(db_conn):
    '''TC-orders-014: \u975e\u5df2\u53d6\u6d88\u8ba2\u5355\u5b8c\u6210\u65f6\u95f4\u975e\u7a7a\u65f6\u89c4\u5219\u4e0d\u9002\u7528\u6821\u9a8c\u901a\u8fc7.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1014)
    fields = {
        'order_id': 1014,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 66.0,
        'status': '\u5f85\u6536\u8d27',
        'created_at': '2024-06-13 09:00:00',
        'completed_at': '2024-05-20 08:00:00',
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is not None:
        pytest.fail(f'\u89c4\u5219\u672a\u843d\u5730: status=\u201c\u5f85\u6536\u8d27\u201d\u4e0d\u9002\u7528 RULE-orders-003\uff0c\u4f46\u63d2\u5165\u88ab\u62d2\u7edd: {err}')
    row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1014,)).fetchone()
    assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u6210\u529f\u540e\u672a\u67e5\u8be2\u5230 order_id=1014 \u7684\u8bb0\u5f55'


def test_tc_orders_015(db_conn):
    '''TC-orders-015: \u4e70\u5bb6\u4e0e\u5356\u5bb6\u4e0d\u540c\u65f6\u6821\u9a8c\u901a\u8fc7.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1015)
    fields = {
        'order_id': 1015,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 45.0,
        'status': '\u5f85\u53d1\u8d27',
        'created_at': '2024-06-14 09:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is not None:
        pytest.fail(f'\u89c4\u5219\u672a\u843d\u5730: buyer_id=7 \u4e0e seller_id=29 \u4e0d\u76f8\u7b49\uff0c\u4f46\u63d2\u5165\u88ab\u62d2\u7edd: {err}')
    row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1015,)).fetchone()
    assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u6210\u529f\u540e\u672a\u67e5\u8be2\u5230 order_id=1015 \u7684\u8bb0\u5f55'


def test_tc_orders_016(db_conn):
    '''TC-orders-016: \u4e70\u5bb6\u6216\u5356\u5bb6\u4ec5\u4e00\u65b9\u4e3a NULL \u65f6\u6821\u9a8c\u7ed3\u679c\u5f85\u786e\u8ba4.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1016)
    fields = {
        'order_id': 1016,
        'product_id': 1,
        'buyer_id': None,
        'seller_id': 29,
        'deal_price': 45.0,
        'status': '\u5f85\u53d1\u8d27',
        'created_at': '2024-06-14 09:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is None:
        row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1016,)).fetchone()
        assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u88ab\u63a5\u53d7\u4f46\u672a\u67e5\u8be2\u5230 order_id=1016 \u7684\u8bb0\u5f55'
        assert row['buyer_id'] is None
        assert row['seller_id'] == 29
    # \u88ab\u62d2\u7edd\u4e5f\u540c\u6837\u53ef\u63a5\u53d7\uff1aNULL \u8fb9\u754c\u9700\u4e1a\u52a1\u786e\u8ba4


def test_tc_orders_017(db_conn):
    '''TC-orders-017: \u4e70\u5bb6\u4e0e\u5356\u5bb6\u5747\u4e3a NULL \u65f6\u6821\u9a8c\u7ed3\u679c\u5f85\u786e\u8ba4.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1017)
    fields = {
        'order_id': 1017,
        'product_id': 1,
        'buyer_id': None,
        'seller_id': None,
        'deal_price': 45.0,
        'status': '\u5f85\u53d1\u8d27',
        'created_at': '2024-06-14 09:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is None:
        row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1017,)).fetchone()
        assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u88ab\u63a5\u53d7\u4f46\u672a\u67e5\u8be2\u5230 order_id=1017 \u7684\u8bb0\u5f55'
        assert row['buyer_id'] is None
        assert row['seller_id'] is None
    # \u88ab\u62d2\u7edd\u4e5f\u540c\u6837\u53ef\u63a5\u53d7\uff1aNULL \u8fb9\u754c\u9700\u4e1a\u52a1\u786e\u8ba4


def test_tc_orders_018(db_conn):
    '''TC-orders-018: \u4e70\u5bb6\u4e0e\u5356\u5bb6\u76f8\u540c\u65f6\u6821\u9a8c\u5931\u8d25.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1018)
    fields = {
        'order_id': 1018,
        'product_id': 1,
        'buyer_id': 54,
        'seller_id': 54,
        'deal_price': 45.0,
        'status': '\u5f85\u53d1\u8d27',
        'created_at': '2024-06-14 09:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is None:
        pytest.fail('\u89c4\u5219\u672a\u843d\u5730: buyer_id=54 \u4e0e seller_id=54 \u76f8\u7b49\uff0c\u8fdd\u53cd\u201c\u4e70\u5bb6\u4e0e\u5356\u5bb6\u4e0d\u80fd\u662f\u540c\u4e00\u4eba\u201d\uff0c\u4f46\u6570\u636e\u5e93\u63a5\u53d7\u4e86\u63d2\u5165')


def test_tc_orders_019(db_conn):
    '''TC-orders-019: \u8ba2\u5355\u72b6\u6001\u4e3a\u5f85\u4ed8\u6b3e\u65f6\u6821\u9a8c\u901a\u8fc7.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1019)
    fields = {
        'order_id': 1019,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 45.0,
        'status': '\u5f85\u4ed8\u6b3e',
        'created_at': '2024-06-16 09:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is not None:
        pytest.fail(f'\u89c4\u5219\u672a\u843d\u5730: status=\u201c\u5f85\u4ed8\u6b3e\u201d\u5c5e\u4e8e\u679a\u4e3e\u503c\uff0c\u4f46\u63d2\u5165\u88ab\u62d2\u7edd: {err}')
    row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1019,)).fetchone()
    assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u6210\u529f\u540e\u672a\u67e5\u8be2\u5230 order_id=1019 \u7684\u8bb0\u5f55'


def test_tc_orders_020(db_conn):
    '''TC-orders-020: \u8ba2\u5355\u72b6\u6001\u4e3a\u5f85\u53d1\u8d27\u65f6\u6821\u9a8c\u901a\u8fc7.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1020)
    fields = {
        'order_id': 1020,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 45.0,
        'status': '\u5f85\u53d1\u8d27',
        'created_at': '2024-06-16 10:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is not None:
        pytest.fail(f'\u89c4\u5219\u672a\u843d\u5730: status=\u201c\u5f85\u53d1\u8d27\u201d\u5c5e\u4e8e\u679a\u4e3e\u503c\uff0c\u4f46\u63d2\u5165\u88ab\u62d2\u7edd: {err}')
    row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1020,)).fetchone()
    assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u6210\u529f\u540e\u672a\u67e5\u8be2\u5230 order_id=1020 \u7684\u8bb0\u5f55'


def test_tc_orders_021(db_conn):
    '''TC-orders-021: \u8ba2\u5355\u72b6\u6001\u4e3a\u5f85\u6536\u8d27\u65f6\u6821\u9a8c\u901a\u8fc7.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1021)
    fields = {
        'order_id': 1021,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 45.0,
        'status': '\u5f85\u6536\u8d27',
        'created_at': '2024-06-16 11:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is not None:
        pytest.fail(f'\u89c4\u5219\u672a\u843d\u5730: status=\u201c\u5f85\u6536\u8d27\u201d\u5c5e\u4e8e\u679a\u4e3e\u503c\uff0c\u4f46\u63d2\u5165\u88ab\u62d2\u7edd: {err}')
    row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1021,)).fetchone()
    assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u6210\u529f\u540e\u672a\u67e5\u8be2\u5230 order_id=1021 \u7684\u8bb0\u5f55'


def test_tc_orders_022(db_conn):
    '''TC-orders-022: \u8ba2\u5355\u72b6\u6001\u4e3a\u5df2\u5b8c\u6210\u65f6\u6821\u9a8c\u901a\u8fc7.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1022)
    fields = {
        'order_id': 1022,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 45.0,
        'status': '\u5df2\u5b8c\u6210',
        'created_at': '2024-06-16 09:00:00',
        'completed_at': '2024-06-16 12:00:00',
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is not None:
        pytest.fail(f'\u89c4\u5219\u672a\u843d\u5730: status=\u201c\u5df2\u5b8c\u6210\u201d\u5c5e\u4e8e\u679a\u4e3e\u503c\uff0c\u4f46\u63d2\u5165\u88ab\u62d2\u7edd: {err}')
    row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1022,)).fetchone()
    assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u6210\u529f\u540e\u672a\u67e5\u8be2\u5230 order_id=1022 \u7684\u8bb0\u5f55'


def test_tc_orders_023(db_conn):
    '''TC-orders-023: \u8ba2\u5355\u72b6\u6001\u4e3a\u5df2\u53d6\u6d88\u65f6\u6821\u9a8c\u901a\u8fc7.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1023)
    fields = {
        'order_id': 1023,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 45.0,
        'status': '\u5df2\u53d6\u6d88',
        'created_at': '2024-06-16 13:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is not None:
        pytest.fail(f'\u89c4\u5219\u672a\u843d\u5730: status=\u201c\u5df2\u53d6\u6d88\u201d\u5c5e\u4e8e\u679a\u4e3e\u503c\uff0c\u4f46\u63d2\u5165\u88ab\u62d2\u7edd: {err}')
    row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1023,)).fetchone()
    assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u6210\u529f\u540e\u672a\u67e5\u8be2\u5230 order_id=1023 \u7684\u8bb0\u5f55'


def test_tc_orders_024(db_conn):
    '''TC-orders-024: \u8ba2\u5355\u72b6\u6001\u4e3a NULL \u65f6\u6821\u9a8c\u5931\u8d25.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1024)
    fields = {
        'order_id': 1024,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 45.0,
        'status': None,
        'created_at': '2024-06-17 09:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is None:
        pytest.fail('\u89c4\u5219\u672a\u843d\u5730: status=NULL \u4e0d\u5728\u4e94\u4e2a\u679a\u4e3e\u503c\u4e2d\uff0c\u4f46\u6570\u636e\u5e93\u63a5\u53d7\u4e86\u63d2\u5165')


def test_tc_orders_025(db_conn):
    '''TC-orders-025: \u8ba2\u5355\u72b6\u6001\u4e3a\u7a7a\u5b57\u7b26\u4e32\u65f6\u6821\u9a8c\u5931\u8d25.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1025)
    fields = {
        'order_id': 1025,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 45.0,
        'status': '',
        'created_at': '2024-06-17 10:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is None:
        pytest.fail('\u89c4\u5219\u672a\u843d\u5730: status=\'\' \u4e0d\u5c5e\u4e8e\u4efb\u4f55\u679a\u4e3e\u503c\uff0c\u4f46\u6570\u636e\u5e93\u63a5\u53d7\u4e86\u63d2\u5165')


def test_tc_orders_026(db_conn):
    '''TC-orders-026: \u8ba2\u5355\u72b6\u6001\u4e3a\u679a\u4e3e\u5916\u4e2d\u6587\u503c\u65f6\u6821\u9a8c\u5931\u8d25.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1026)
    fields = {
        'order_id': 1026,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 45.0,
        'status': '\u5df2\u5173\u95ed',
        'created_at': '2024-06-18 09:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is None:
        pytest.fail('\u89c4\u5219\u672a\u843d\u5730: status=\u201c\u5df2\u5173\u95ed\u201d\u4e0d\u5728\u679a\u4e3e\u5217\u8868\u4e2d\uff0c\u4f46\u6570\u636e\u5e93\u63a5\u53d7\u4e86\u63d2\u5165')


def test_tc_orders_027(db_conn):
    '''TC-orders-027: \u8ba2\u5355\u72b6\u6001\u4e3a\u82f1\u6587\u5927\u5c0f\u5199\u503c\u65f6\u6821\u9a8c\u5931\u8d25.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1027)
    fields = {
        'order_id': 1027,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 45.0,
        'status': 'Cancelled',
        'created_at': '2024-06-18 10:00:00',
        'completed_at': None,
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is None:
        pytest.fail('\u89c4\u5219\u672a\u843d\u5730: status=\'Cancelled\' \u4e0d\u5728\u679a\u4e3e\u5217\u8868\u4e2d\uff0c\u4f46\u6570\u636e\u5e93\u63a5\u53d7\u4e86\u63d2\u5165')


def test_tc_orders_028(db_conn):
    '''TC-orders-028: \u8ba2\u5355\u72b6\u6001\u5e26\u591a\u4f59\u7a7a\u683c\u65f6\u6821\u9a8c\u5931\u8d25.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1028)
    fields = {
        'order_id': 1028,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 45.0,
        'status': '\u5df2\u5b8c\u6210 ',
        'created_at': '2024-06-19 09:00:00',
        'completed_at': '2024-06-19 12:00:00',
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is None:
        pytest.fail('\u89c4\u5219\u672a\u843d\u5730: status=\u201c\u5df2\u5b8c\u6210 \u201d\u5e26\u5c3e\u90e8\u7a7a\u683c\u4e0e\u679a\u4e3e\u503c\u4e0d\u7cbe\u786e\u5339\u914d\uff0c\u4f46\u6570\u636e\u5e93\u63a5\u53d7\u4e86\u63d2\u5165')


def test_tc_orders_029(db_conn):
    '''TC-orders-029: \u6ee1\u8db3\u5168\u90e8\u89c4\u5219\u7684\u6709\u6548\u8ba2\u5355\u53ef\u6b63\u5e38\u5165\u5e93.'''
    _assert_fields_present(db_conn, 'orders', ORDERS_FIELDS)
    _ensure_product(db_conn)
    _clean_order(db_conn, 1099)
    fields = {
        'order_id': 1099,
        'product_id': 1,
        'buyer_id': 7,
        'seller_id': 29,
        'deal_price': 88.88,
        'status': '\u5df2\u5b8c\u6210',
        'created_at': '2024-06-20 09:00:00',
        'completed_at': '2024-06-25 18:00:00',
    }
    err = _try_insert(db_conn, 'orders', fields)
    if err is not None:
        pytest.fail(f'\u89c4\u5219\u672a\u843d\u5730: \u6ee1\u8db3\u5168\u90e8\u4e94\u6761\u89c4\u5219\u7684\u8ba2\u5355\u63d2\u5165\u88ab\u62d2\u7edd: {err}')
    row = db_conn.execute('SELECT * FROM orders WHERE order_id = ?', (1099,)).fetchone()
    assert row is not None, '\u89c4\u5219\u672a\u843d\u5730: \u63d2\u5165\u6210\u529f\u540e\u672a\u67e5\u8be2\u5230 order_id=1099 \u7684\u8bb0\u5f55'
    assert row['deal_price'] == pytest.approx(88.88)
    assert row['status'] == '\u5df2\u5b8c\u6210'
    assert row['completed_at'] == '2024-06-25 18:00:00'
