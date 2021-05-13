"""Django_shopping URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from merchant import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index),
    # 商家模块
    path('merchant/index/', views.index),
    path('merchant/merchantLogin/', views.merchantLogin),
    path('merchant/merchantLogout/', views.merchantLogout),
    path('merchant/createMerchant/', views.createMerchant),
    path('merchant/merchantHome/', views.merchantHome),
    path('merchant/addGoods/', views.addGoods),
    path('merchant/showOrders/', views.showOrders),
    path('merchant/deleteGoods/<int:goodsID>/', views.deleteGoods),
    path('merchant/updateGoods/<int:goodsID>/', views.updateGoods),
    path('merchant/goodsDetails/<int:goodsID>/', views.goodsDetails),
    path('merchant/selfInfoMerch/<int:merchantID>/', views.selfInfoMerch),
    # 用户模块
    path('customer/customerLogin/', views.customerLogin),
    path('customer/createCustomer/', views.createCustomer),
    path('customer/customerHome/', views.customerHome),
    path('customer/customerLogout/', views.customerLogout),
    path('customer/customerGoodsDetails/<int:goodsID>/', views.customerGoodsDetails),
    path('customer/customerCart/',views.customerCart),
    path('customer/addToCart/<int:goodsID>/', views.addToCart),
    path('customer/selfInfoCus/', views.selfInfoCus),
    path('customer/customerOrder/', views.customerOrder),
    path('customer/confirmOrder/', views.confirmOrder),
    path('customer/deleteCart/<int:goodsID>/', views.deleteCart),
    path('customer/confirmGoods/<int:orderID>/', views.confirmGoods),
    path('customer/judgement/<int:goodsID>/',views.addComments),#*******
    path('customer/submitComplaints/<int:orderID>',views.submitComplaints),
    path('customer/updateComplaints/', views.updateComplaints),
    path('customer/visualPay/<int:orderID>', views.visualPay),
    path('customer/pay/', views.pay),
    path('customer/goodInfoCus/', views.customerHome),
    # 管理员模块
    path('admin/adminIndex/', views.adminIndex),
    path('admin/adminLogout/', views.adminLogout),
    path('admin/complaints/', views.complaints),
    path('admin/dealComp/<int:compID>', views.dealComp),

    path('admin/frozeIndex/', views.frozeIndex),
    path('admin/updatefroze/', views.updatefroze),

    path('admin/discount/', views.discount),
    path('admin/updateDiscount/', views.updateDiscount),

]
