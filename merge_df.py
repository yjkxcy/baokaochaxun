import pandas as pd
import numpy as np



dtypes={'学校代号': np.int32,
	    '学校名称': str,
	    '专业代号': np.int32,
	    '专业名称': str,
	    '计划数': np.int32,
	    '分数线': np.int32,
	    # '位次': np.int64
	   }
columns = ['学校代号', '学校名称', '专业代号', '专业名称', '计划数', '分数线', '位次']
nodisplaycol = ['学校代号', '专业代号', '学校名称_x', '学校名称_y']
mergecol = ['学校代号', '学校名称', '专业名称']
mergekeys = ['学校代号', '专业名称']
renamecol = ['计划数', '分数线', '位次']
year_2022 = [[1, '浙江大学（一流大学建设高校）', 1, '人文科学试验班', 85, 663, 3573],
			 [1, '浙江大学（一流大学建设高校）', 2, '新闻传播学类', 59, 664, 3329],
			 [1, '浙江大学（一流大学建设高校）', 3, '外国语言文学类', 10, 665, 3044],
			 [1, '浙江大学（一流大学建设高校）', 6, '社会科学试验班', 182, 668,2479]
			]

year_2021 = [[1, '浙江大学(一流大学建设高校)', 1, '人文科学试验班', 201, 662, 3548],
			 [1, '浙江大学(一流大学建设高校)', 2, '社会科学试验班', 188, 667, 2356],
			 [1, '浙江大学(一流大学建设高校)', 3, '社会科学试验班(竺可桢学院人文社科实验班、智能财务班)', 3, 686, 350],
			 [1, '浙江大学(一流大学建设高校)', 4, '理科试验班类', 108, 667, 2397]
			]




def setDisplayType():
	'''打印效果设置'''
	pd.set_option('display.max_rows', None)
	pd.set_option('display.max_columns', None)
	pd.set_option('display.width', None)
	pd.set_option('display.max_colwidth', None)
	pd.set_option('display.unicode.ambiguous_as_wide', True)  #对齐
	pd.set_option('display.unicode.east_asian_width', True)   #对齐


def fillschool(df):
	if df['学校名称_x']:
		return df['学校名称_x']
	else:
		return df['学校名称_y']
	# return df['学校名称_x'] if df['学校名称_x'] == '' else df['学校名称_y']

def renameCol(df, suffix):
	'''重命名dataframe列名'''
	columns = ['计划数', '分数线', '位次']
	df.rename(columns={key:f'{key}_{suffix}' for key in columns}, inplace=True)

def displayCol(columns):
	'''返回需显示的列'''
	notDisCol = ['学校代号', '专业代号', '学校名称']
	for col in columns:
		if 'x' in col or 'y' in col:
			columns.remove(col)



if __name__ == '__main__':
	setDisplayType()
	# df1 = pd.DataFrame(year_2022, columns=columns, dtype=dtypes)
	df1 = pd.read_excel(r'C:\Users\user\Desktop\报考\2022年一段投档线.xls')
	renameCol(df1, '2022')
	df1['位次_2022'].fillna(0)
	df1['位次_2022'].astype(np.int64)
	print(df1.dtypes)
	df2 = pd.DataFrame(year_2021, columns=columns)
	renameCol(df2, '2021')
	mergecol.extend(f'{key}_2021' for key in renamecol)
	year = 2022
	lastyear = 2021
	suffix = [f'_{year}', f'_{lastyear}']
	df_m = pd.merge(df1, df2, on=mergekeys, how='outer').replace(np.NaN, '')
	# df_m = pd.merge(df1, df2[mergecol], on=mergekeys, how='outer').replace(np.NaN, '')
	# df_m = pd.merge(df1, df2[mergecol], on=mergekeys, how='outer', suffixes=suffix).replace(np.NaN, '')
	# df_m = pd.merge(df1, df2[mergecol], on=mergekeys, how='left').replace(np.NaN, '')
	# df_m = pd.merge(df1, df2[mergecol], on=mergekeys, how='inner')
	newcol = df_m.columns.tolist()
	newcol.insert(1, '学校名称')
	# print(newcol)
	df_m['学校名称'] = df_m.apply(fillschool, axis=1)
	df_m = df_m.reindex(columns=newcol)
	displaycol = list(df_m.columns)  #df.columns.tolist()
	print(displaycol)
	displayCol(displaycol)

	# for delvalue in nodisplaycol:
		# displaycol.remove(delvalue)
	print(displaycol)
	# print(df_m[displaycol].to_string(index=False))
	# print(df_m['schoolname'].to_string(index=False))