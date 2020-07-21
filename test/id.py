# t代表身份证号码的位数，w表示每一位的加权因子


tet = IdCardAuth()
rest = tet.check_true("50010619910107212x")
print(rest)