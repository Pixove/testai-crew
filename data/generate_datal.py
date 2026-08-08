import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('zh_CN')
conn = sqlite3.connect('campus_trade.db')
cursor = conn.cursor()

# ==================== 1. 建表 ====================
cursor.executescript('''
DROP TABLE IF EXISTS favorites;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS students;

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY,
    name TEXT, 
    major TEXT, 
    grade TEXT, 
    phone TEXT, 
    wechat TEXT, 
    register_time TEXT
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    seller_id INTEGER,
    title TEXT, 
    category TEXT, 
    price REAL, 
    original_price REAL,
    condition TEXT, 
    status TEXT,
    created_at TEXT,
    FOREIGN KEY(seller_id) REFERENCES students(student_id)
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    product_id INTEGER,
    buyer_id INTEGER, 
    seller_id INTEGER,
    deal_price REAL, 
    status TEXT,
    created_at TEXT, 
    completed_at TEXT,
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);

CREATE TABLE reviews (
    review_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    reviewer_id INTEGER, 
    target_id INTEGER,
    rating INTEGER, 
    content TEXT,
    created_at TEXT
);

CREATE TABLE favorites (
    favorite_id INTEGER PRIMARY KEY,
    student_id INTEGER,
    product_id INTEGER,
    created_at TEXT
);
''')


# ==================== 2. 标题生成函数（品牌与品类严格绑定）====================
def generate_realistic_title(category: str) -> str:
    """根据类别生成真实感商品标题（品牌与品类严格绑定）"""
    
    if category == '教材':
        books = ['高等数学', '线性代数', '概率论', '大学英语', '数据结构', '操作系统', 
                 '计算机网络', '数据库原理', '软件工程', '离散数学', '经济学原理', 
                 '会计学基础', '心理学导论', '法律基础', '管理学原理', '市场营销']
        editions = ['第2版', '第3版', '第4版', '第5版', '修订版']
        templates = [
            f"{random.choice(books)} {random.choice(editions)}",
            f"{random.choice(books)} {random.choice(editions)} 带笔记",
            f"{random.choice(books)} 全新未拆封",
            f"{random.choice(books)} {random.choice(editions)} 几乎全新",
            f"{random.choice(books)} 含习题册"
        ]
        return random.choice(templates)
    
    elif category == '电子产品':
        # 严格绑定：品牌 → 该品牌真实生产的产品
        brand_products = {
            '华为': ['手机', '平板', '耳机', '笔记本', '显示器', '智能手表'],
            '小米': ['手机', '平板', '耳机', '笔记本', '智能手表', '充电宝', '音箱'],
            '苹果': ['手机', '平板', '笔记本', '耳机', '智能手表'],
            '索尼': ['耳机', '音箱', '相机', '游戏机'],
            '三星': ['手机', '平板', '耳机', '显示器', '智能手表'],
            '联想': ['笔记本', '平板', '显示器'],
            '戴尔': ['笔记本', '显示器'],
            '惠普': ['笔记本', '显示器'],
            '漫步者': ['耳机', '音箱'],
            '罗技': ['键盘', '鼠标', '音箱']
        }
        specs = ['128GB', '256GB', '512GB', '8GB', '16GB', 'Pro', 'Max']
        
        brand = random.choice(list(brand_products.keys()))
        device = random.choice(brand_products[brand])
        
        templates = [
            f"{brand} {device} {random.choice(specs)}",
            f"{brand} {device} 带配件",
            f"{brand} {device} 轻微划痕",
            f"{brand} {device} 使用一年"
        ]
        return random.choice(templates)
    
    elif category == '服饰':
        # 严格绑定：品牌 → 该品牌主营的服饰品类
        brand_clothings = {
            '优衣库': ['T恤', '卫衣', '外套', '牛仔裤', '衬衫', '羽绒服'],
            'ZARA': ['T恤', '卫衣', '外套', '牛仔裤', '衬衫', '连衣裙'],
            'H&M': ['T恤', '卫衣', '外套', '牛仔裤', '衬衫', '连衣裙'],
            '耐克': ['T恤', '卫衣', '外套', '运动鞋', '短袖'],
            '阿迪达斯': ['T恤', '卫衣', '外套', '运动鞋', '短袖'],
            '安踏': ['T恤', '卫衣', '外套', '运动鞋'],
            '李宁': ['T恤', '卫衣', '外套', '运动鞋'],
            '美特斯邦威': ['T恤', '卫衣', '外套', '牛仔裤', '衬衫'],
            '森马': ['T恤', '卫衣', '外套', '牛仔裤'],
            '以纯': ['T恤', '卫衣', '外套', '牛仔裤']
        }
        sizes = ['S', 'M', 'L', 'XL', 'XXL']
        
        brand = random.choice(list(brand_clothings.keys()))
        clothing = random.choice(brand_clothings[brand])
        
        templates = [
            f"{brand} {clothing} {random.choice(sizes)}",
            f"{clothing} {random.choice(sizes)} 全新带吊牌",
            f"{clothing} {random.choice(sizes)} 仅试穿",
            f"{clothing} {random.choice(sizes)} 几乎全新"
        ]
        return random.choice(templates)
    
    elif category == '生活用品':
        items = ['台灯', '电风扇', '电热水壶', '吹风机', '收纳箱', '衣架', '镜子', '闹钟', '雨伞', '背包', '小电锅', '储物盒', '拖鞋', '鞋柜', '晾衣杆']
        templates = [
            f"{random.choice(items)}",
            f"全新 {random.choice(items)}",
            f"{random.choice(items)} 使用痕迹较明显",
            f"{random.choice(items)} 九成新"
        ]
        return random.choice(templates)
    
    elif category == '体育用品':
        sports = ['篮球', '足球', '羽毛球拍', '乒乓球拍', '哑铃', '瑜伽垫', '跳绳', '护腕', '游泳镜', '滑板', '轮滑鞋', '登山杖']
        templates = [
            f"{random.choice(sports)} 九成新",
            f"{random.choice(sports)} 带包装",
            f"全新 {random.choice(sports)}",
            f"{random.choice(sports)} 使用次数少"
        ]
        return random.choice(templates)
    
    else:  # 其他
        others = ['收纳盒', '装饰品', '花瓶', '相框', '插排', '置物架', '挂钩', '纸巾盒', '香薰', '手电筒', '钥匙扣']
        templates = [
            f"{random.choice(others)} 全新未拆",
            f"{random.choice(others)} 几乎全新",
            f"{random.choice(others)} 未使用"
        ]
        return random.choice(templates)


def get_price_range(category: str) -> tuple:
    """根据类别返回价格范围"""
    ranges = {
        '教材': (5, 60),
        '电子产品': (50, 1800),
        '生活用品': (5, 200),
        '服饰': (10, 200),
        '体育用品': (10, 350),
        '其他': (5, 150)
    }
    return ranges.get(category, (5, 100))


# ==================== 3. 生成数据 ====================
print("⏳ 开始生成数据...")

categories = ['教材', '电子产品', '生活用品', '服饰', '体育用品', '其他']
conditions = ['全新', '几乎全新', '有使用痕迹', '较旧']
statuses = ['在售', '已预定', '已售出']

# 3.1 学生（80人）
students = []
majors = ['计算机科学', '软件工程', '电子信息', '数学', '物理', '化学', '生物', 
          '医学', '法学', '经济学', '金融学', '会计学', '英语', '新闻学', '艺术设计']
grades = ['大一', '大二', '大三', '大四', '研究生']

for i in range(1, 81):
    students.append({
        'id': i,
        'name': fake.name(),
        'major': random.choice(majors),
        'grade': random.choices(grades, weights=[0.2, 0.25, 0.25, 0.2, 0.1])[0],
        'phone': fake.phone_number(),
        'wechat': fake.user_name() + str(random.randint(10, 99)),
        'register_time': fake.date_time_between(start_date='-2y', end_date='now').isoformat()
    })

cursor.executemany(
    'INSERT INTO students VALUES (:id, :name, :major, :grade, :phone, :wechat, :register_time)',
    students
)
print(f"  ✅ 学生: {len(students)} 条")

# 3.2 商品（300件）
products = []
for i in range(1, 301):
    seller = random.choice(students)
    category = random.choice(categories)
    min_price, max_price = get_price_range(category)
    price = round(random.uniform(min_price, max_price), 2)
    
    products.append({
        'id': i,
        'seller_id': seller['id'],
        'title': generate_realistic_title(category),
        'category': category,
        'price': price,
        'original_price': round(price * random.uniform(1.5, 3.5), 2),
        'condition': random.choice(conditions),
        'status': random.choices(statuses, weights=[0.5, 0.15, 0.35])[0],
        'created_at': fake.date_time_between(start_date='-1y', end_date='now').isoformat()
    })

cursor.executemany(
    'INSERT INTO products VALUES (:id, :seller_id, :title, :category, :price, :original_price, :condition, :status, :created_at)',
    products
)
print(f"  ✅ 商品: {len(products)} 条")

# 3.3 订单（400条）
orders = []
for i in range(1, 401):
    product = random.choice(products)
    potential_buyers = [s for s in students if s['id'] != product['seller_id']]
    buyer = random.choice(potential_buyers)
    status = random.choices(['待付款', '待发货', '待收货', '已完成', '已取消'], 
                           weights=[0.1, 0.15, 0.2, 0.4, 0.15])[0]
    created = fake.date_time_between(start_date='-6m', end_date='now')
    completed = created + timedelta(days=random.randint(1, 14)) if status == '已完成' else None
    
    orders.append({
        'id': i,
        'product_id': product['id'],
        'buyer_id': buyer['id'],
        'seller_id': product['seller_id'],
        'deal_price': round(product['price'] * random.uniform(0.8, 1.0), 2),
        'status': status,
        'created_at': created.isoformat(),
        'completed_at': completed.isoformat() if completed else None
    })

cursor.executemany(
    'INSERT INTO orders VALUES (:id, :product_id, :buyer_id, :seller_id, :deal_price, :status, :created_at, :completed_at)',
    orders
)
print(f"  ✅ 订单: {len(orders)} 条")

# 3.4 评价（已完成订单的70%有评价）
reviews = []
review_id = 1
review_contents = ['很好', '不错', '一般', '性价比高', '描述相符', '发货快', 
                   '质量很好', '卖家态度好', '物流很快', '和描述一致', '超值', 
                   '挺满意的', '还不错', '有点小瑕疵但能接受', '好评', '非常满意']
for order in orders:
    if order['status'] == '已完成' and random.random() < 0.7:
        reviews.append({
            'id': review_id,
            'order_id': order['id'],
            'reviewer_id': order['buyer_id'],
            'target_id': order['seller_id'],
            'rating': random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.05, 0.15, 0.3, 0.45])[0],
            'content': random.choice(review_contents),
            'created_at': order['completed_at']
        })
        review_id += 1

cursor.executemany(
    'INSERT INTO reviews VALUES (:id, :order_id, :reviewer_id, :target_id, :rating, :content, :created_at)',
    reviews
)
print(f"  ✅ 评价: {len(reviews)} 条")

# 3.5 收藏（400条）
favorites = []
for i in range(1, 401):
    student = random.choice(students)
    product = random.choice(products)
    favorites.append({
        'id': i,
        'student_id': student['id'],
        'product_id': product['id'],
        'created_at': fake.date_time_between(start_date='-3m', end_date='now').isoformat()
    })

cursor.executemany(
    'INSERT INTO favorites VALUES (:id, :student_id, :product_id, :created_at)',
    favorites
)
print(f"  ✅ 收藏: {len(favorites)} 条")


# ==================== 4. 提交并关闭 ====================
conn.commit()
conn.close()

print("\n" + "=" * 50)
print("✅ 校园二手交易平台数据生成完成！")
print("=" * 50)
print(f"📁 数据库文件: campus_trade.db")
print("\n📊 数据统计:")
print(f"  👤 学生: 80 人")
print(f"  📦 商品: 300 件")
print(f"  📋 订单: 400 条")
print(f"  ⭐ 评价: {len(reviews)} 条")
print(f"  ❤️  收藏: 400 条")
print("=" * 50)