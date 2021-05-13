from django.contrib.auth.models import User
from django.db import models

class Customer(models.Model):
    # 导入auth_user数据表，id，账号，密码，姓名均存储在这里面;账户是否被冻结由is_active属性决定
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    # 昵称
    niname = models.CharField(max_length=30)
    # 性别
    gender = models.CharField(max_length=10,default=0)
    # 手机号
    phone = models.CharField(max_length=16)
    # 其他信息，可按需要自行补充
    # address
    address = models.CharField(max_length=128, default=0)

# 用户-地址联系集
class Addresses(models.Model):
    # 用户ID（外键）
    cusID = models.IntegerField()

    # 地址字段
    addr = models.CharField(max_length=100)
    # 其他信息，可按需要自行补充


# 用户—购物车联系集（购物车）
class Cart(models.Model):
    # 用户ID（外键）
    cusID = models.IntegerField()
    # 商品ID
    goodsID = models.IntegerField()
    # 商品数量
    goodsNum = models.IntegerField()
    # 其他信息，可按需要自行补充


# 用户-订单-商家联系集
class OrdersCus(models.Model):
    # 用户ID（外键）
    cusID = models.IntegerField()
    # 商家ID
    mercID = models.IntegerField()
    # 订单ID（外键）
    ordID = models.IntegerField()
    # 其他信息，可按需要自行补充


# 用户-商家联系集（关注的店铺）
class MerchCus(models.Model):
    # 用户ID（外键）
    cusID = models.IntegerField()
    # 商家ID
    mercID = models.IntegerField()
    # 其他信息，可按需要自行补充

# Create your models here.
class Merchant(models.Model):
    # 导入auth_user数据表，id，账号，密码，姓名均存储在这里面;账户是否被冻结由is_active属性决定
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    # 店铺名称

    merchantName = models.CharField(max_length=50, blank=True)
    # 收入
    income = models.FloatField(blank=True, default=0)
    # 店铺好评率，这里暂时用字符串定义，也可以用数字类型，需要增加计算模块
    reputation = models.CharField(max_length=50, blank=True)


    # 其他信息，可按需要自行补充
    # 在原来auth_user表的字段的基础上添加出新的字段
    phone = models.CharField(max_length=16, blank=True)

# 商家-商品联系集（商家所售卖的商品）
class MerchGoods(models.Model):
    # 商家ID
    merchID = models.IntegerField()
    # 商品ID
    goodsID = models.IntegerField()
    # 其他信息，可按需要自行补充


# 商家-订单联系集
class MerchOrders(models.Model):
    # 商家ID
    merchID = models.IntegerField()
    # 订单ID
    orderID = models.IntegerField()
    # 其他信息，可按需要自行补充


# 管理员模块
class Admin(models.Model):
    # 导入auth_user数据表，id，账号，密码，姓名均存储在这里面;账户是否被冻结由is_active属性决定
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    # 其他信息，可按需要自行补充


# 投诉模块，只有管理员可以进行操作
class Complaints(models.Model):
    # 投诉信息ID
    id = models.AutoField(primary_key='True')
    # 投诉用户ID
    cusID = models.IntegerField()
    # 所投诉订单，根据这个ID可以查询到被投诉商家及商品的信息
    orderID = models.IntegerField()
    # 投诉内容
    content = models.TextField()
    # 状态 0:未处理  1:已处理
    status = models.IntegerField(default=0)
    # 其他信息，可按需要自行补充


# 商品模块
class Goods(models.Model):
    # 商品ID
    id = models.AutoField(primary_key='True')
    # 商家ID（外键）
    merchID = models.IntegerField()
    # 商品名称
    goodsName = models.CharField(max_length=32)
    # 商品图片(参数需自行添加)
    image = models.CharField(max_length=128)
    # 商品价格
    price = models.FloatField(default=0.0)
    # 商品类型（标签）
    type = models.CharField(max_length=32)
    # 商品库存（剩余数量）
    num = models.IntegerField()
    # 商品描述
    description = models.TextField('商品描述', max_length=255)
    # 商品状态，0为未冻结（可以出售），1为冻结（不可出售）；商品数量小于1也可以看做是冻结状态
    goodsSta = models.IntegerField(default=0)
    # 商品状态，0为未冻结（可以出售），1为冻结（不可出售）
    frozen = models.IntegerField(default=0)
    # 其他信息，可按需要自行补充


# 商品-评价联系集
class CommentonGood(models.Model):
    # 商品ID(外键)
    goodsID = models.IntegerField()
    # 用户ID
    cusID = models.IntegerField()
    # 评价内容
    content = models.TextField()
    # 评价星级，0-5共6档
    rate = models.IntegerField()
    # 其他信息，可按需要自行补充


# 订单模块
class Order(models.Model):
    # 订单ID
    id = models.AutoField(primary_key='True')
    # 商家ID
    merchID = models.IntegerField(default=0)
    # 顾客ID
    cusID = models.IntegerField(default=0)
    # 商品ID
    goodsID = models.IntegerField(default=0)
    # 订单创建时间
    starttime = models.DateTimeField(auto_now=False, auto_now_add=True)
    # 订单最后修改时间
    modtime = models.DateTimeField(auto_now=True, auto_now_add=False)
    # 收货地址
    address = models.CharField(max_length=100)
    # 运输状态，0为未发货，1为已发货，2为已收货
    transSta = models.IntegerField(default=0)
    # 售后状态，0为未申请售后，1为申请售后中，2为售后服务完成
    afterSta = models.IntegerField(default=0)
    # 修改状态，0为不可修改，1为可修改
    modSta = models.IntegerField(default=0)
    # 购买商品数量
    goodsNum = models.IntegerField(default=1)
    # 支付金额
    price = models.FloatField(default=0.0)
    # 其他信息，可按需要自行补充
    # 付款状态,-1为未激活,0为未付款，1为可付款
    paySta = models.IntegerField(default=0)
