import re
import numpy as np
import pandas as pd
from itertools import product
from copy import deepcopy
from pathlib import Path
# from pprint import pprint
# from functools import reduce 
# from pandas.api.types import is_string_dtype, is_numeric_dtype, is_float_dtype


#命令行提示信息
promptMsg = {
	'学校名称': '学校名称，多个输入间使用空格分隔[浙江大学]',
	'专业名称': '专业名称，多个输入间使用空格分隔[计算机]',
	'分数线': '分数线[600或610-615]',
	'位次': '位次范围[100或980-1000]',
	'学校代号': '学校所属地区，多个输入间使用空格分隔[浙江]'
}

#省(市、自治区)代码
schoolCode = {
	'浙江': ('00', '01', '02', '03'),
	'北京': ('11'),
	'天津': ('12'),
	'河北': ('13'),
	'山西': ('14'),
	'内蒙古': ('15'),
	'辽宁': ('21'),
	'吉林': ('22'),
	'黑龙江': ('23'),
	'上海': ('31'),
	'江苏': ('32', '33'),
	'安徽': ('34'),
	'福建': ('35'),
	'江西': ('36'),
	'山东': ('37'),
	'湖北': ('40', '41'),
	'河南': ('42'),
	'湖南': ('43'),
	'广东': ('44'),
	'广西': ('45'),
	'海南': ('46'),
	'重庆': ('50'),
	'四川': ('51'),
	'贵州': ('52'),
	'云南': ('53'),
	'西藏': ('54'),
	'陕西': ('61'),
	'甘肃': ('62'),
	'青海': ('63'),
	'宁夏': ('64'),
	'新疆': ('65'),
	'香港': ('81'),
	'军校': ('90'),
}

def setDisplayType():
	'''打印效果设置'''
	pd.set_option('display.max_rows', None)
	pd.set_option('display.max_columns', None)
	pd.set_option('display.width', None)
	pd.set_option('display.max_colwidth', None)
	pd.set_option('display.unicode.ambiguous_as_wide', True)  #对齐
	pd.set_option('display.unicode.east_asian_width', True)   #对齐

def userConfirm(description):
	'''用户确认
	   :param description: 提示用户输入的信息
	   :return: 返回 'y' 或 'n'
	'''
	while True:
		inputstr = input(description).strip().lower()
		if inputstr in ('Y', 'y', 'N', 'n'):
			return inputstr
		print(r'无效输入，请重新输入！')

def inputNum(description, convert=int):
	'''包装了input异常处理'''
	try:
		return convert(input(description).strip())
	except ValueError as err:
		pass

def parserNumVal(value):
	'''解析输入的数字
	   :param value: 用户的输入 '630', '638-668'
	   :return: 返回元组 (630, 630), (638, 668)，不合规输入返回None
	'''
	if re.match(r'^\d+$', value):  #如：638
		return value, value
	elif re.match(r'^(\d+)-(\d+)$', value):   #如：620-645
		return re.match(r'^(\d+)-(\d+)$', value).group(0).split('-')

def inputRange(description):
	'''数字范围合规性检测
	   :param : 用户的输入 '630', '638-668'
	   :return: 返回字符串类型 '630-630', '638-668'，不合规输入返回None
	'''
	result = parserNumVal(input(description).strip())
	if result:
		return f'{result[0]}-{result[1]}'

def inputStr(description):
	'''处理字符串输入
	   :param : 用户的输入 '浙江大学 南京大学'
	   :return: 返回元组 ['浙江大学', '南京大学']，不合规输入返回None

	'''
	return input(description).strip().split()  #去除两边空格并分隔多个输入值

def inputCode(description):
	'''地区编码映射
	   :param : 用户的输入 '浙江 上海 江苏'
	   :return: 返回元组 ['0-999', '3100-3199', '3200-3399']，不合规输入返回None

	'''
	regions = input(description).strip().split()   #[浙江，上海，江苏]
	res = []
	for region in regions:
		if region == '浙江':
			res.append('0-999')
		elif region == '江苏':
			res.append('3200-3399')
		elif region == '湖北':
			res.append('4000-4199')
		elif region in schoolCode.keys():
			res.append(f'{schoolCode[region]}00-{schoolCode[region]}99')
	return res

class ConsoleMenu(object):
	'''控制台风格菜单
	   :param menuitem: 显示的菜单项，如：['学校代号', '学校名称', '专业名称', '分数线', '位次']
	'''
	def __init__(self, menuitem):
		self._menuiten = list(menuitem)

	def countNum(self, chars):
		'''统计字符串中的数字数量'''
		return len(re.findall(r'\d', chars))

	def showMenuBar(self):
		'''显示菜单栏'''
		separate = 5   #间隔
		prefix = 3     #前缀
		border = 5
		length = sum([len(x)*2-self.countNum(x)+prefix for x in self._menuiten]) + len(self._menuiten)*separate + border*2 + separate
		print(f"\n{'*'*length}")
		print(f"{'*'*border}", end='')
		for num, value in enumerate(self._menuiten):
			print(f'{" "*5}{num}: {value}', end='')
		print(f"{' '*separate}{'*'*border}")
		print(f"{'*'*length}\n")	

	def choice(self, description):
		'''返回用户选择的菜单项'''
		self.showMenuBar()
		res = inputNum(f'{description}[0-{len(self._menuiten)-1}]:')
		while res not in range(len(self._menuiten)):
			res = inputNum(f'输入有误,{description}[0-{len(self._menuiten)-1}]:')
		return self._menuiten[res]   # 返回值 '学校名称 '

class UserInput(object):
	'''获取用户选择的菜单项和需查询的信息
	   :param optionItem: 可供选择的查询项
	   :param yearItem: 可供查询的年份
	   :return : 返回用户的输入信息
	'''
	def __init__(self, optionItem, yearItem):
		self._optionItem = optionItem
		self._yearItem = yearItem

	def singleOption(self):
		'''用户选择的一条查询项'''
		selectCol = ConsoleMenu(self._optionItem).choice('请输入查询字段的序号')
		if selectCol in ('学校名称', '专业名称'):
			input1 = inputStr
		elif selectCol == '学校代号':
			input1 = inputCode
		elif selectCol in ('分数线', '位次'):
			input1 = inputRange
		searchValue = input1(f'请输入{promptMsg[selectCol]}:')
		while not searchValue:
			searchValue = input1(f'输入有误请重新输入{promptMsg[selectCol]}:')
		print(searchValue)
		return {selectCol:searchValue}

	@property
	def selectOptions(self):
		'''用户选择的查询项'''
		options = dict.fromkeys(self._optionItem, None)
		options.update(self.singleOption())
		while True:
			if userConfirm(r'还需要输入更多查询项吗[Y/N]:') == 'y':
				options.update(self.singleOption())
			else:
				break
		return options

	@property
	def selectYear(self):
		'''查询的年份'''
		return ConsoleMenu(self._yearItem).choice('请输入查询的年份')

class ColgAdmInfo(object):
	'''读取Excel文件生成dataframe数据，提供多维度报考信息查询'''
	columns = ['学校代号', '学校名称', '专业名称', '分数线', '位次']  #类变量 可供查询的字段

	def __init__(self, scorefile):
		self._df = self.readExcel(scorefile)

	def readExcel(self, scorefile):
		try:
			return pd.read_excel(scorefile)
		except Exception as err:
			pass

	def _toNum(self, choiceStr):
		'''字符串格式的查询项转成数字格式'''
		return [int(s) for s in choiceStr.split('-')]

	def _xuexiao(self, name):
		'''学校名称'''
		if name:
			return self._df['学校名称'].str.contains(name)
		return np.repeat(True, len(self._df.index))

	def _zhuanye(self, name):
		'''专业名称'''
		if name:
			return self._df['专业名称'].str.contains(name)
		return np.repeat(True, len(self._df.index))

	def _fenshu(self, value):
		'''分数线'''
		if value:
			start, end = self._toNum(value)
			return (self._df['分数线'] >= start) & (self._df['分数线'] <= end)
		return np.repeat(True, len(self._df.index))

	def _weici(self, value):
		'''位次'''
		if value:
			start, end = self._toNum(value)
			return (self._df['位次'] >= start) & (self._df['位次'] <= end) 
		return np.repeat(True, len(self._df.index))

	def _daihao(self, value):
		'''学校代号'''
		if value:
			start, end = self._toNum(value)
			return (self._df['学校代号'] >= start) & (self._df['学校代号'] <= end) 
		return np.repeat(True, len(self._df.index))

	def search(self, options):
		'''返回查询结果'''
		return self._df[self._xuexiao(options.get('学校名称', None))
						& self._zhuanye(options.get('专业名称', None))
						& self._fenshu(options.get('分数线', None))
						& self._weici(options.get('位次', None))
						& self._daihao(options.get('学校代号', None))]

	def display(self):
		'''终端打印输出'''
		print(self._df.to_string(index=False))

def backfill(item, option):
	'''根据新的选择项生成查询项'''
	tmp = deepcopy(option)
	# print('option', option)
	# print('item', item)
	for v in item:
		for key, value in tmp.items():
			if value and (v in value):
				tmp[key] = v
	# print(tmp)
	return tmp

# {'学校代号': ['浙江'], '学校名称': ['浙江大学'], '专业名称': ['信息'], '分数线': '600-700', '位次': '1-10000'}

def combiOption(option):
	'''对用户输入的学校名称和专业名称排列组合
	param option: {'学校名称': ['浙江大学','南京大学'], '专业名称': ['计算机','信息'], '学校代号': None, '分数线': '600-635', '位次': None}
	return: [{'学校代号': 'None', '学校名称': '浙江大学', '专业名称': '计算机', '分数线': '600-635', '位次': None}
			 {'学校代号': 'None', '学校名称': '浙江大学', '专业名称': '信息', '分数线': '600-635', '位次': None}
			 {'学校代号': 'None', '学校名称': '南京大学', '专业名称': '计算机', '分数线': '600-635', '位次': None}
			 {'学校代号': 'None', '学校名称': '南京大学', '专业名称': '信息', '分数线': '600-635', '位次': None}
			]
	'''
	result = []
	tmp = []
	for key, value in option.items():
		if value and (key in ('学校名称', '专业名称', '学校代号')):
			tmp.append(value)
	for choice in product(*tmp):
		result.append(backfill(choice, option))
	return result

#弃用（封装意义不大）
class CollegeData(object):
	'''往年大学的招生分数线信息'''
	def __init__(self, fileList, screener=None):
		self._scoreDF = {}
		self._screener = screener   #筛选条件
		self._initData(fileList)

	def _initData(fileList):
		'''初始化查询数据库'''
		for fname in fileList:
			key = Path(fname).stem
			print(key)
			self._scoreDF[key] = ColgAdmInfo(fname)

def yearSearch(colgadminfo, options):
	'''年度查询'''
	dfs = []
	for option in options:
		dfs.append(colgadminfo.search(option))  #保存每次查询结果
	return pd.concat(dfs).drop_duplicates(['专业名称', '学校名称'])   #返回合并后的查询 去重处理


def main(score_df):
	quitFlag = False  #退出查询程序标志
	userinput = UserInput(optionItem = ColgAdmInfo.columns,  yearItem = scoreDict.keys())
	options = combiOption(userinput.selectOptions)  #接收用户输入的查询选项
	# searchResult = {}
	searchResult = []
	while True:
		year = userinput.selectYear                 #用户输入的要查询的年份
		resnew = yearSearch(score_df[year], options)
		if resnew.empty:
			print(r'没有搜索到相关信息')
		else:
			# searchResult[year] = resnew
			searchResult.append(resnew)
			print(resnew.to_string(index=False))  #输出查询结果，不打印index
		quitFlag = True if userConfirm(r'继续查询吗[Y/N]:') != 'y' else False
		if quitFlag:
			break
	# needCol = ['学校代号', '专业名称', '计划数', '分数线', '位次']
	# merge_df = pd.merge(searchResult[0], searchResult[1][needCol], on=['专业名称', '学校代号'])
	# print(merge_df.to_string(index=False))
 

if __name__ == '__main__':
	fpath = Path.cwd()     #投档文件保存路径
	# fpath = r'C:\Users\user\Desktop\报考'     #投档文件保存路径
	scoreDict = {
		'2020年一段线': '2020年一段投档线.xls',
		'2021年一段线': '2021年一段投档线.xls',
		'2022年一段线': '2022年一段投档线.xls'
	}
	setDisplayType()      # 显示效果设置
	score_df = {}
	for key, value in scoreDict.items():
		score_df[key] = ColgAdmInfo(Path(fpath, value))
	main(score_df)

