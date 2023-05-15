import gradio as gr
import pandas as pd
from pathlib import Path
from score_search import *


helper= '''
		    ### 使用说明：
		       * 学校代号 指省、市、自治区，支持多个输入，如 “浙江 上海”。
		       * 学校名称 非完全匹配，只需输入的内容包含在校名中，支持多输入，如 “浙江大学 南京大学”。
		       * 专业名称 非完全匹配，只需输入的内容包含在专业名中，支持多输入，如 “计算机 软件”。
		       * 分数线   支持范围输入，如 “655”、 “650-680”
		       * 位次     支持范围输入，如 “6000”、 “6100-6800”

		'''

def mapNumRange(num):
	'''数字范围合规性检测
	   :param : 用户的输入 '630', '638-668'
	   :return: 返回字符串类型 '630-630', '638-668'，不合规输入返回None
	'''
	result = parserNumVal(num)
	if result:
		return f'{result[0]}-{result[1]}'
	else:
		return ''

def mapCode(regions):
	'''学校代号转换 [浙江，上海，江苏] to ['0-999', '3100-3199', '3200-3399']'''
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

def showres(score_df, args):
	'''返回查询的数据'''
	print(args)
	year = list(args).pop()
	if args.count('') < 5:
		input_opt = {}
		input_opt['学校代号'] = mapCode(args[0].strip().split())
		input_opt['学校名称'] = args[1].strip().split()
		input_opt['专业名称'] = args[2].strip().split()
		input_opt['分数线'] = mapNumRange(args[3].strip())
		input_opt['位次'] = mapNumRange(args[4].strip())
		print(input_opt)
		options = combiOption(input_opt)
		res = yearSearch(score_df[year], options)
		return res
	# return pd.DataFrame([['浙江大学', '计算机应用技术', '238', '655', '6800']],
						 # columns=['学校名称', '专业名称', '计划数', '分数线', '位次'])

def clear_input(*args):
	'''清空查询值'''
	return ['' for _ in args]

def main(score_df):
	with gr.Blocks() as demo:
		# gr.Markdown("# 浙江省2020-2022高考一段线信息查询系统")
		gr.Markdown("# 浙江省2020-2022大学一段线录取信息查询系统")
		gr.Markdown(helper)
		with gr.Row():
			schcode = gr.Textbox(label="学校代号") #, value="浙江")
			school = gr.Textbox(label="学校名称") #, value="杭州电子科技")
			major = gr.Textbox(label="专业名称") #, value="计算机 软件")
		with gr.Row():
			score = gr.Textbox(label="分数线") #, value="600-650")
			ranking = gr.Textbox(label="位次") #, value="10000-13000")
		with gr.Row():
			# year = gr.Radio(list(score_df.keys()), label="查询年份", value="2022年一段线")
			year = gr.Radio(["2022年一段线", "2021年一段线", "2020年一段线"], label="查询年份", value="2022年一段线")
		with gr.Row():
			query_btn = gr.Button("查询")
			clear_btn = gr.Button("清空")
		board = gr.Dataframe(value=[["", "", "", "", ""]] * 5,
							 interactive=False,
							 headers=['学校名称', '专业名称', '计划数', '分数线', '位次'], wrap=True) # wrap 自动换行

		query_btn.click(lambda *input_data: showres(score_df, input_data),
						inputs=[schcode, school, major, score, ranking, year],
						outputs=board)
		clear_btn.click(clear_input, inputs=[schcode, school, major, score, ranking],
						outputs=[schcode, school, major, score, ranking])

	demo.launch()



if __name__ == '__main__':
	fpath = Path.cwd()     #投档文件保存路径，默认当前目录
	scoreDict = {
		'2020年一段线': '2020年一段投档线.xls',
		'2021年一段线': '2021年一段投档线.xls',
		'2022年一段线': '2022年一段投档线.xls'
	}
	score_df = {}
	for key, value in scoreDict.items():
		score_df[key] = ColgAdmInfo(Path(fpath, value))
	main(score_df)
