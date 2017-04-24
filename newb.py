# -*- coding: utf-8 -*-
import re
# print((800001 / 800001) * 1000)
#
# #最高阅读数
# print((100001 / 100001) * 1000)
#
# #平均
# print (100001 / 100001) * 1000
#
# #头条
# print (100001 / 100001) * 1000
#
# #点赞
# print (24226 / 24226) *1000
#
# print (0.75*1000) + (0.05*1000) + (0.1*1000) + (0.05* 1000) + (0.05* 1000)

# print (100001/(100000+1))
# print (100001/(100000+1))
# print (100001/(100000+1))
# print (100001/(100000+1))
# print (73004/(80000)) #0.9
#
# print (0.75*1000)+(0.05*1000)+(0.1*1000)+(0.05*1000) +(0.05*900)

regstr = '{src:"3",ver:"1",timestamp:"1492077766",signature:"BuDT-Hh747T4nGy6HyHbK4UfB-aXvmGxFyBGgNd9txZIiwxX9wY-87SZrSCpo4ck2kPWex7x*y4y-ogCqNezF-YpKx6vma609RjnsTJDxppgYABaLVN3g5fKBT6tDLz9sSSTkkKhXdkh0cjFvTKP8lk1Wa0-p4qYPibv9HC2Tr4="}'

sg_data = (u'3', u'1', u'1492079128', u'BuDT-Hh747T4nGy6HyHbKwx6gcy9GrSf8GIMFZGF8yAUvyCPCJjX9rrugg1ZKUo6t3i9VqCTKZMWaKr6JND-p*mPjeSwmC9dboCfDLbOx8yf2cp2GT7gxQR1jNA*A8rO8OL9P-liFaRMa75B2LQTr5m-*qGwUJfMDjoPoEb8gfA=')
# s = re.findall(u'{src:"(.*?)",ver:"(.*?)",timestamp:"(.*?)",signature:"(.*?)"}', regstr)
print (list(sg_data))
sg_data = list(sg_data)
print (sg_data[0])
