import os
import uuid
from urllib.parse import unquote
from django.utils.encoding import smart_str
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# Create your views here.
from pytz import unicode

from merchant.models import Merchant, Goods, Order, Customer, Cart, OrdersCus, Complaints, CommentonGood

# 索引页面
def index(request):
    return render(request, 'index.html')

# 商家登录
def merchantLogin(request):
    if request.POST:
        # 接收参数
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        # 去数据库进行认证
        # 说白了就是根据账号, 密码 去auth_user数据表进行匹配
        user = authenticate(username=username, password=password)

        if user is None:
            return render(request, 'merchantLogin.html', {'msg': '登录验证失败,...'})
        merchantID = user.id
        merchants = Merchant.objects.filter(user_id=merchantID)

        if len(merchants) == 0:
            return render(request, 'merchantLogin.html', {'msg': '请到对应的入口登录！'})
        else:
            # 存在该用户, 则进行登录
            # 这里的login函数, 主要是hi为了把登录的对象存入到django_session表
            login(request, user)
            # 响应到客户端

            merchantID = request.user.id
            merchant = Merchant.objects.filter(user_id=merchantID)[0]
            allGoods = Goods.objects.filter(merchID=merchantID)
            context = dict()
            context['goodsList'] = allGoods
            context['username'] = merchant.merchantName

            return redirect('/merchant/merchantHome/', context)
            # return render(request, )
    else:
        return render(request, 'merchantLogin.html')

# 商家主页面
def merchantHome(request):
    merchantID = request.user.id
    merchant = Merchant.objects.filter(user_id=merchantID)[0]
    allGoods = Goods.objects.filter(merchID=merchantID)
    context = dict()
    context['goodsList'] = allGoods
    context['username'] = merchant.merchantName
    context['merchantID'] = merchantID
    return render(request, 'merchantHome.html', context)

# 注册商家账号
def createMerchant(request):
    if request.POST:
        # 获取参数
        username = request.POST.get('username', None)
        merchantName = request.POST.get('merchantName', None)
        password = request.POST.get('password', None)
        password2 = request.POST.get('password2', None)
        phone = request.POST.get('phone', None)

        # 判断用户是否存在
        user = User.objects.filter(username=username)

        if len(user) > 0:
            return render(request, 'createMerchant.html', {'error_msg': '用户名已经被使用'})
        elif password != password2:
            return render(request, 'createMerchant.html', {'error_msg': '密码不一致'})
        elif len(password) == 0:
            return render(request, 'createMerchant.html', {'error_msg': '密码不能为空'})
        # 这是用户名可以使用的时候
        # 向django_user数据表种添加数据
        user = User.objects.create_user(username=username, password=password)
        # 向Merchant表中添加数据
        merchant = Merchant()
        # 这是建立外键的一对一关系
        merchant.user_id = user.id
        merchant.merchantName = merchantName
        # 这是为phone属性赋值
        merchant.phone = phone
        merchant.save()
        return render(request, 'merchantLogin.html', {'msg': '创建成功，请登录'})
    else:

        return render(request, 'createMerchant.html')

# 商家上传商品
@login_required
def addGoods(request):
    if request.POST:
        goodsName = request.POST.get('goodsName', None)
        price = request.POST.get('price', None)
        type = request.POST.get('type', None)
        num = request.POST.get('num', None)
        description = request.POST.get('description', None)
        image = request.FILES.get('image', None)

        # 获取登录商家的ID
        merchID = request.user.id
        print(goodsName)
        # 文件名
        imgFileName = image.name
        # 文件大小
        imgFileSize = image.size
        # 文件后缀
        imgFileStuff = os.path.splitext(imgFileName)[1]

        # 模拟可以上传的文件的类型列表
        allowedTypes = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

        # 判断上传文件是否受限
        if imgFileStuff.lower() not in allowedTypes:
            # 需要响应到前台说一声, '文件格式不对'
            return render(request, 'addGoods.html', {'error_msg': '图片格式不正确'})
            # 生成唯一名称
        picuploadUniqueName = str(uuid.uuid1()) + imgFileStuff

        # 验证上传到服务器的目录是否存在
        uploadPath = os.path.join(os.getcwd(), 'merchant/static/images/goods')

        if not os.path.exists(uploadPath):
            os.mkdir(uploadPath)
            print('成功创建文件存储目录')
        else:
            print('服务器中已经存在该目录')

        # 设置上传文件的全路径
        uploadAbsPath = uploadPath + os.sep + picuploadUniqueName
        print('文件的全名称: {0}'.format(uploadAbsPath))

        try:
            with open(uploadAbsPath, 'wb+') as fp:
                for chunk in image.chunks():
                    fp.write(chunk)
        except:
            return render(request, 'addGoods.html', {'error_msg': '上传失败'})

        # 图片显示路径
        picurl = 'images/goods/' + picuploadUniqueName
        print('文件picurl:' + picurl)

        goods = Goods()
        goods.merchID = merchID
        goods.goodsName = goodsName
        goods.price = price
        goods.type = type
        goods.num = num
        goods.description = description
        goods.image = picurl
        goods.save()

        context = dict()
        context['success_msg'] = '上传成功'
        context['picurl'] = picurl
        context['picsize'] = imgFileSize
        return render(request, 'addGoods.html', context)

    else:
        return render(request, 'addGoods.html')

# 商家更新商品
@login_required
def updateGoods(request, goodsID):
    if request.POST:
        image = request.FILES.get('image', None)
        if image == None:
            Goods.objects.filter(id=goodsID).update(
                price=request.POST.get('price'),
                goodsName=request.POST.get('goodsName'),
                type=request.POST.get('type'),
                num=request.POST.get('num'),
                description=request.POST.get('description'),
            )
        else:
            # 文件名
            imgFileName = image.name

            # 文件后缀
            imgFileStuff = os.path.splitext(imgFileName)[1]

            # 模拟可以上传的文件的类型列表
            allowedTypes = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

            # 判断上传文件是否受限
            if imgFileStuff.lower() not in allowedTypes:
                # 需要响应到前台说一声, '文件格式不对'
                return render(request, 'updateGoods.html', {'error_msg': '图片格式不对'})

            # 可以生成文件的唯一标识名称
            picuploadUniqueName = str(uuid.uuid1()) + imgFileStuff

            # 设置文件上传到服务器的目录地址
            uploadPath = os.path.join(os.getcwd(), 'merchant/static/images/goods')

            if not os.path.exists(uploadPath):
                os.mkdir(uploadPath)
                print('创建上传目录成功')
            else:
                print('服务器原本就从在该目录')

            # 设置上传文件的全路径
            picFileAbsPath = uploadPath + os.sep + picuploadUniqueName
            print('上传图片的全名称: {0}'.format(picFileAbsPath))

            try:
                with open(picFileAbsPath, 'wb+') as fp:
                    # 分块处理
                    for chunk in image.chunks():
                        fp.write(chunk)
            except:
                return render('updateGood.html', {'error_msg', '图片上传失败'})

            picurl = 'images/goods/' + picuploadUniqueName

            Goods.objects.filter(id=goodsID).update(
                price=request.POST.get('price'),
                goodsName=request.POST.get('goodsName'),
                type=request.POST.get('type'),
                num=request.POST.get('num'),
                description=request.POST.get('description'),
                image=picurl
            )
        # 向数据库更新
        return redirect('/merchant/merchantHome/')
    else:
        context = dict()
        goodsList = Goods.objects.filter(id=goodsID)
        context['goods'] = goodsList[0]
        return render(request, 'updateGoods.html', context)

# 删除商品
@login_required
def deleteGoods(request, goodsID):
    Goods.objects.filter(id=goodsID).delete()
    return redirect('/merchant/merchantHome/')


# 商家页面展示订单
@login_required
def showOrders(request):
    # 获取当前登录的商家的ID
    merchantID = request.user.id
    # 获取所有订单的ID
    orderList = Order.objects.filter(merchID=merchantID)

    # 根据订单编号获取商品信息
    goodsList = Goods.objects.none()
    for order in orderList:
        goodsList = goodsList | Goods.objects.filter(id=order.goodsID)

    merchant = Merchant.objects.get(user_id=merchantID)
    income = merchant.income

    context = dict()
    context['orderList'] = orderList
    context['goodsList'] = goodsList
    context['income'] = income
    return render(request, 'showOrders.html', context)

# 商品详情
@login_required
def goodsDetails(request, goodsID):
    # 获取所有与所选商品相关的评价
    commentList = CommentonGood.objects.filter(goodsID=goodsID)
    customerList = Customer.objects.none()
    # 获取所有与该商品评论相关的顾客对象
    for comment in commentList:
        customerList = customerList | Customer.objects.filter(id=comment.cusID)
        c = Customer.objects.all()

    context = dict()
    goodsList = Goods.objects.filter(id=goodsID)
    context['commentList'] = commentList
    context['goods'] = goodsList[0]
    return render(request, 'goodsDetails.html', context)

# 商家登出
@login_required
def merchantLogout(request):
    # 安全退出的函数
    # 主要是清除在django_session表中的登录对象数据
    logout(request)
    return render(request, 'merchantLogin.html')

# 商家个人信息
@login_required
def selfInfoMerch(request, merchantID):
    if request.POST:
        # 获取当前登录的商家的ID
        phone = request.POST.get('phone')
        merchantName = request.POST.get('merchantName')
        user = User.objects.get(id=merchantID)
        merchant = Merchant.objects.get(user_id=merchantID)
        Merchant.objects.filter(user_id=merchantID).update(merchantName=merchantName, phone=phone)
        username = user.username
        income = merchant.income
        isMerchant = 1
        context = {'merchantID': merchantID, 'username': username, 'phone': phone, 'merchantName': merchantName,
                   'income': income,
                   'isMerchant': isMerchant, 'success_msg': '信息修改成功！'}
        return render(request, 'selfInfoMerch.html', context)
    else:
        # 获取当前登录的商家对象
        user = User.objects.get(id=merchantID)
        merchant = Merchant.objects.get(user_id=merchantID)
        username = user.username
        phone = merchant.phone
        income = merchant.income
        merchantName = merchant.merchantName
        isMerchant = 1
        context = {'merchantID': merchantID, 'username': username, 'phone': phone, 'merchantName': merchantName,
                   'income': income,
                   'isMerchant': isMerchant}
        return render(request, 'selfInfoMerch.html', context)

# 顾客登录
def customerLogin(request):
    if request.POST:
        # 接收参数
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        # 去数据库进行认证
        # 说白了就是根据账号, 密码 去auth_user数据表进行匹配
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'customerLogin.html', {'msg': '登录验证失败,...'})
        customerID = user.id
        customers = Customer.objects.filter(user_id=customerID)

        if len(customers) == 0:
            return render(request, 'customerLogin.html', {'msg': '请到对应的入口登录！'})
        else:

            # 存在该用户, 则进行登录
            # 这里的login函数, 主要是hi为了把登录的对象存入到django_session表
            login(request, user)
            # 响应到客户端
            customer = customers[0]
            customerID = request.user.id
            allGoods = Goods.objects.all()
            context = dict()
            context['goodsList'] = allGoods
            context['username'] = customer.niname

            return redirect('/customer/customerHome/')
    else:
        return render(request, 'customerLogin.html')

# 生成顾客（注册）
def createCustomer(request):
    if request.POST:
        # 获取参数
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        password2 = request.POST.get('password2', None)
        nickname = request.POST.get('nickname', None)
        gender = request.POST.get('gender', None)
        phone = request.POST.get('phone', None)
        address = request.POST.get('address', None)

        # 判断用户是否存在
        user = User.objects.filter(username=username)

        if len(user) > 0:
            return render(request, 'createCustomer.html', {'error_msg': '用户名已经被使用'})
        elif password != password2:
            return render(request, 'createCustomer.html', {'error_msg': '密码不一致'})
        elif len(password) == 0:
            return render(request, 'createCustomer.html', {'error_msg': '密码不能为空'})

        # 这是用户名可以使用的时候
        # 向django_user数据表种添加数据
        user = User.objects.create_user(username=username, password=password)
        # 向userProfile表中添加数据
        login(request, user)
        profile = Customer()
        # 这是建立外键的一对一关系
        profile.user_id = user.id
        profile.niname = nickname
        profile.gender = gender
        profile.phone = phone
        profile.address = address
        # 这是为phone属性赋值
        profile.save()

        return render(request, 'customerLogin.html', {'success_msg': '创建用户成功,请登录'})
    else:
        return render(request, 'createCustomer.html')


def customerLogout(request):
    logout(request)
    return render(request, 'customerLogin.html')

# 顾客主页面
@login_required
def customerHome(request):
        customerID = request.user.id

    # 获取顾客对象
        customer = Customer.objects.filter(user_id=customerID)[0]

    # 获取所有商品
        # allGoods = Goods.objects.all()
        context = dict()
        # context['goodsList'] = allGoods
        context['username'] = customer.niname
        print(customer.niname)
        context['customerID'] = customerID
        # return render(request, 'customerHome.html', context)
        # frozenMerchList = Merchant.objects.filter(frozen=1)
        frozenGoodList = Goods.objects.filter(frozen=1)
        print(frozenGoodList)

        goodsName = request.POST.get('goodsName', "__None__")
        print(goodsName)
        if goodsName == "__None__":
            goodsName = request.COOKIES.get('goodsName')
        if goodsName and not goodsName == "__None__":
            goodsList = Goods.objects.filter(goodsName__icontains=goodsName)
        else:
            goodsList = Goods.objects.all()
        print(goodsList)

        goodListT = Goods.objects.none()
        for good in goodsList:
            if good not in frozenGoodList:
                goodListT = goodListT | Goods.objects.filter(id=good.pk)
                print(Goods.objects.get(id=good.pk).goodsName)
        goodsList = goodListT

        orderWay = request.POST.get('orderWay')
        if not orderWay:
            orderWay = request.COOKIES.get('orderWay')
        if orderWay == "priceUpper":
            goodsList = goodsList.order_by("price")
        elif orderWay == "priceLower":
            goodsList = goodsList.order_by("-price")
        else:
            goodsList = goodsList.order_by("id")


        # 把数据集合响应到前端
        context['goodsList'] = goodsList
        context['orderWay'] = orderWay
        context['goodsName'] = goodsName
        # return render(request, 'customerHome.html', context)
        resp = render(request, "customerHome.html", context)
        resp.set_cookie('orderWay', orderWay, max_age=3600)

        #goodsName = unquote(unicode(goodsName).encode("utf-8"))
        #goodsName = smart_str(goodsName)
        resp.set_cookie('goodsName', bytes(goodsName, 'utf-8').decode('ISO-8859-1'), max_age=3600)

        return resp



# 顾客商品详情
@login_required
def customerGoodsDetails(request, goodsID):
    # 获取所有与该商品相关的评论
    commentList = CommentonGood.objects.filter(goodsID=goodsID)
    customerList = Customer.objects.none()
    for comment in commentList:
        print(comment.cusID)
        customerList = customerList | Customer.objects.filter(id=comment.cusID)
        c = Customer.objects.all()

    context = dict()
    goodsList = Goods.objects.filter(id=goodsID)
    context['commentList'] = commentList
    context['goods'] = goodsList[0]
    return render(request, 'customerGoodsDetails.html', context)

# 顾客购物车
@login_required
def customerCart(request):
    cartList = Cart.objects.filter(cusID=request.user.id)
    goodsList = Goods.objects.none()
    # 获取所有与该顾客相关的商品
    for cart in cartList:
        goodsList = goodsList | Goods.objects.filter(id=cart.goodsID)

    context = dict()
    context['goodsList'] = goodsList
    context['cartList'] = cartList

    return render(request, 'customerCart.html', context)

# 加入购物车
@login_required
def addToCart(request, goodsID):
    cusID = request.user.id
    Cart.objects.create(cusID=cusID, goodsNum=1, goodsID=goodsID)
    nums = Cart.objects.all()
    print('数组' + str(len(nums)))
    return redirect('/customer/customerHome/')


# 顾客个人信息
@login_required
def selfInfoCus(request):
    if request.POST:
        # 获取当前登录的商家的ID
        customerID = request.user.id
        phone = request.POST.get('phone')
        niname = request.POST.get('niname')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        user = User.objects.get(id=customerID)
        Customer.objects.filter(user_id=customerID).update(phone=phone, niname=niname, gender=gender, address=address)
        customer = Customer.objects.get(user_id=customerID)
        username = user.username
        context = {'customer': customer, 'username': username, 'msg': '信息修改成功！'}
        return render(request, 'selfInfoCus.html', context)
    else:
        customer = Customer.objects.get(user_id=request.user.id)
        user = User.objects.get(id=request.user.id)
        username = user.username
        return render(request, 'selfInfoCus.html', {'customer': customer, 'username': username})

# 确认订单
@login_required
def confirmOrder(request):
    if request.POST:
        tem = request.POST.getlist('check')
        cartList = Cart.objects.none()
        orderList = Order.objects.none()
        goodsList = Goods.objects.none()
        # 订单总金额
        sum = int(0)
        for goodstem in tem:
            cartList = cartList | Cart.objects.filter(goodsID=goodstem)
        for goodstem in tem:
            goodsList = goodsList | Goods.objects.filter(id=goodstem)
        # 这里没有设置订单地址
        for carttem in cartList:
            for goodstem in goodsList:
                if (carttem.goodsID == goodstem.id):
                    customertem = Customer.objects.get(user_id=carttem.cusID)
                    tem = Order(goodsID=carttem.goodsID, goodsNum=carttem.goodsNum, address=customertem.address,
                                paySta=-1, transSta=0, afterSta=0, modSta=1,cusID=customertem.user_id, merchID=goodstem.merchID,
                                price=int(carttem.goodsNum) * int(goodstem.price))
                    tem.save()
                    orinum = Goods.objects.get(id=goodstem.id).num
                    newnum = orinum-1
                    Goods.objects.filter(id=goodstem.id).update(num=newnum)
                    tem1 = OrdersCus(cusID=carttem.cusID, mercID=goodstem.merchID, ordID=tem.id)
                    tem1.save()
                    sum = sum + tem.price
                    orderList = orderList | Order.objects.filter(id=tem.id)
                    Cart.objects.get(id=carttem.id).delete()
        orderList = orderList.filter(paySta=-1)
        context = dict()
        context['sum'] = sum
        context['goodsList'] = goodsList
        context['orderList'] = orderList
        return render(request, 'confirmOrder.html', context)
    else:
        return render(request, 'confirmOrder.html')


# 从购物车删除
@login_required
def deleteCart(request, goodsID):
    Cart.objects.filter(goodsID=goodsID).delete()
    return redirect("/customer/customerCart/")


# 用户订单
@login_required
def customerOrder(request):
    ordertem = OrdersCus.objects.filter(cusID=request.user.id)

    orderlist = Order.objects.none()
    goodList = Goods.objects.none()
    complist = Complaints.objects.none()

    for tem in ordertem:
        orderlist = orderlist | Order.objects.filter(id=tem.ordID)
        goodList = goodList | Goods.objects.filter(id=Order.objects.get(id=tem.ordID).goodsID)
        complist = Complaints.objects.filter(orderID=tem.ordID)
    # 若订单已被投诉过，则修改订单售后状态
    for ordertem in orderlist:
        for comptem in complist:
            if ordertem.id == comptem.orderID:
                ordertem.afterSta = comptem.status

    context = dict()
    context['orderlist'] = orderlist
    context['goodList'] = goodList
    return render(request, 'customerOrder.html', context)

# 确认收货
def confirmGoods(request,orderID):
    Order.objects.filter(id=orderID).update(transSta=2)
    tem = Order.objects.get(id=orderID)
    oriincome = Merchant.objects.get(user_id=tem.merchID).income
    nowincome = oriincome + tem.price
    Merchant.objects.filter(user_id=tem.merchID).update(income=nowincome)
    goodsID=Order.objects.get(id=orderID).goodsID
    return redirect("/customer/judgement/" + str(goodsID))

# 添加评论
def addComments(request,goodsID):
    goods=Goods.objects.get(id=goodsID)
    print(goodsID)
    context=dict()
    context['goods']=goods
    context['content']="__None__"
    currCus= Customer.objects.get(user_id=request.user.id).id

    if CommentonGood.objects.filter(goodsID=goodsID,cusID=currCus).exists():
        context['content']=CommentonGood.objects.get(goodsID=goodsID,cusID=currCus).content
        return render(request, 'judgement.html', context)

    if request.POST:
        url = '/customer/customerGoodsDetails/' + str(goodsID) + '/'
        print(url)
        textComment = request.POST.get('temp_judgement', None)
        rateStar = request.POST.get('group2', None)

        CommentonGood.objects.create(goodsID=goodsID,cusID=currCus,content=textComment,rate=rateStar)


        return redirect(url)

    return render(request, 'judgement.html', context)

# 提交投诉
def submitComplaints(request,orderID):
    context=dict()
    Order.objects.filter(id=orderID).update(afterSta=1)
    order=Order.objects.get(id=orderID)
    context['order']= order
    context['goods']= Goods.objects.get(id=order.goodsID)
    context['customer']=Customer.objects.get(user_id=request.user.id)
    return render(request,"submitComplaints.html", context)

# 更新投诉结果
def updateComplaints(request):
    if request.POST:
        orderID = request.POST.get('orderID', None)
        customerID = request.POST.get('customerID', None)
        goodsID = request.POST.get('goodsID', None)
        currComplaints = request.POST.get('currComplaints', None)
        goods = Goods.objects.get(id=goodsID)
        order = Order.objects.get(id=orderID)
        order.afterSta=1
        order.save()
        Complaints.objects.create(cusID=int(customerID),orderID=int(orderID),content=currComplaints,status=0)
    return render(request,"submitComplaints.html",{'msg':"投诉成功", 'goods': goods})

# 支付页面
def visualPay(reqeust,orderID):
    Order.objects.filter(id=orderID).update(paySta=1)
    return redirect("/customer/pay/")

# 支付 ?
def pay(request):
    return render(request,'pay.html')

#管理员主页 √
def adminIndex(request):
    return render(request, 'adminIndex.html')
# 管理员登出
def adminLogout(request):
    return render(request, 'index.html')

# 从管理员主页跳转到冻结商品/商家
def frozeIndex(request):
    goodsList=Goods.objects.all()
    merchList=Merchant.objects.all()

    context=dict()
    context['goodsList']=goodsList
    context['merchList']=merchList

    return render(request, 'frozeIndex.html', context)

# 从管理员主页跳转到平台优惠
def discount(request):
    return render(request, 'discount.html')

# 全局变量
theDiscount = 1.0

# 全平台打折优惠
def updateDiscount(request):
    global theDiscount
    goodsList=Goods.objects.all()
    for goods in goodsList:
        goods.price=int(int(goods.price) / float(theDiscount))
        goods.save()
    if request.POST:
        temp = float(request.POST.get('discount_input', None))
        if temp >=0 and temp <= 1.0:
            theDiscount = request.POST.get('discount_input', None)
            goodsList=Goods.objects.all()
            for goods in goodsList:
                goods.price=int(int(goods.price) * float(theDiscount))
                goods.save()
    return render(request, 'discount.html',{'msg':"当前打折率为"+str(theDiscount)})


# 从管理员主页跳转到投诉信息
def complaints(request):
    comListDone=Complaints.objects.filter(status=1)
    comListYet=Complaints.objects.filter(status=0)

    context=dict()
    context['comListDone']=comListDone
    context['comListYet']=comListYet

    return render(request, 'complaints.html' , context)

#=================lyj==========
# 处理投诉
def dealComp(request,compID):
    c=Complaints.objects.get(id=compID)
    c.status=1
    c.save()
    return redirect("/admin/complaints/")

# 更新冻结状态
def updatefroze(request):
    goodList = Goods.objects.all()
    merchList = Merchant.objects.all()

    if request.POST:
        selectName = request.POST.get('selectName', None)
        choose1 = request.POST.get('choose1',None)
        choose2 = request.POST.get('choose2',None)
        selectType = request.POST.get('selectType', None)

        if int(selectType) == 1:
            merchSet = 1
            goodSet = 1
        else:
            merchSet = 0
            goodSet = 0

        id1 = choose1.split(' ',1)[0]
        id2 = choose2.split(' ',1)[0]

        if selectName == 1:
            for merchant in merchList:
                if merchant.id == int(id2):
                    merchant.fronzen=merchSet
                    merchant.save()
                    if merchSet==1:
                        msg="成功冻结Merchant"+str(merchant.id)
                    else:
                        msg="成功解冻Merchant"+str(merchant.id)
        else:
            for good in goodList:
                if good.id == int(id1):
                    good.frozen = goodSet
                    good.save()
                    if merchSet==1:
                        msg="成功冻结Good"+str(good.id)
                    else:
                        msg="成功解冻Good"+str(good.id)
        return render(request, 'frozeIndex.html', {'msg':msg})
    else:
        return render(request, 'frozeIndex.html', {'msg':"无操作结果"})