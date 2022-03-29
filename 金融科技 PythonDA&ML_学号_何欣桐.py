# 在源程序文件同一文件夹下有 data 文件夹，里面存放数据集 excel 文件(含 12746 个基金、一个基金总表)
# 在源程序文件同一文件夹下有 data_new 文件夹，里面存放爬虫得到的 excel 文件(含 100 个基金)
# 在源程序文件同一文件夹下有 src 文件夹，里面存放程序需要的字体文件、浏览器驱动文件、生成的图片、文本文件

if "import模块 ------------------------------------":
    import numpy as np
    import pandas as pd
    import random
    import matplotlib.pyplot as plt
    from pandas.plotting import register_matplotlib_converters

    register_matplotlib_converters()
    from tkinter import ttk
    import tkinter as tk
    import os
    import re
    import requests
    import logging
    from bs4 import BeautifulSoup

    from wordcloud import WordCloud

    import datetime
    from time import sleep

    from selenium import webdriver
    from selenium.webdriver.common.by import By

if "网上抓取基金信息总表 --------------------":
    def crawl_whole_info_table():
        #  一个item_list，也就是一个基金的所有信息(25项,只取0-16项)
        #  ['000227', '华安年年红债券A', 'HANNHZQA', '2020-02-14', '1.0680',
        #  '1.4730', '', '1.6175', '2.8865', '4.2661',
        #  '6.3655','9.3036', '17.2048', '20.9574', '2.9838',
        #  '55.7880', '2013-11-14', '6', '', '0.60%',
        #  '0.06%', '1', '0.06%', '1','30.5295']

        if "1、网上抓取--------------------":
            fund_list = []
            try:
                session = requests.session()
                session.headers["Accept"] = \
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
                session.headers["Accept-Encoding"] = "gzip, deflate, br"
                session.headers["Accept-Language"] = "zh-CN,zh;q=0.9"
                session.headers["Connection"] = "keep-alive"
                session.headers["Upgrade-Insecure-Requests"] = "1"
                session.headers["User-Agent"] = \
                    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
                session.headers["Host"] = "fund.eastmoney.com"
                session.headers["Referer"] = 'http://fund.eastmoney.com/data/fundranking.html'

                for fund_type in ['hh', 'gp', 'zq', 'zs']:
                    # 上面地址中'ft=zq'代表爬取债券型基金，可根据情况更改为pg、gp、hh、zs、QDII、LOF。（偏股型、股票型、混合型、指数型、QDII型、LOF型）
                    url = "http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&ft=%s&rs=&gs=0&qdii=&tabSubtype=,,,,,&pn=10000" % (
                        fund_type)
                    response = session.get(url, verify=False, timeout=60)
                    response.encode = 'utf8'
                    response = response.text
                    """
                    源代码
                    var rankData = {datas:
                        [
                            "970120,兴证资管金麒麟恒睿致远一年持有混合B,XZZGJQLHRZYYNCYHHB,2022-02-11,1.2486,1.6566,-0.66,-0.34,-1.69,,,,,,-3.69,-3.43,2021-12-27,,-3.433875,,,,,,",
                            "970114,兴证资管金麒麟兴睿优选一年持有期混合C,XZZGJQLXRYXYNCYQHHC,2022-02-11,0.9647,0.9647,-0.78,0.34,-3.53,,,,,,-3.53,-3.53,2021-12-13,,-3.53,,0.00%,,,,",
                            ...,
                            "000042,财通中证ESG100指数增强A,CTZZESG100ZSZQA,2022-02-11,1.99,2.4788,-0.82,1.86,-3.89,-3,-3.36,-3.03,52.26,76.72,-5.72,174.67,2013-03-22,1,174.668792,1.20%,0.12%,1,0.12%,1,85.84",
                            "000008,嘉实中证500ETF联接A,JSZZ500ETFLJA,2022-02-11,1.8586,1.9246,-1.31,2.37,-5.13,-5.09,-4.44,5.04,29.08,56.53,-7.87,95.41,2013-03-22,1,95.414295,1.20%,0.12%,1,0.12%,1,13.45"
                        ],
                        allRecords:1622,pageIndex:1,pageNum:10000,allPages:1,allNum:13494,gpNum:2072,hhNum:6738,zqNum:4339,zsNum:1622,bbNum:0,qdiiNum:345,etfNum:0,lofNum:388,fofNum:338};
                    """
                    response = response[response.find('var rankData = {datas:['): response.find(']')]
                    response = response.replace("var rankData = {datas:[", "")
                    for i in response.split('"'):
                        if len(i.split(',')) < 10:
                            continue
                        order = i.split(',')
                        for j in range(4, 16):
                            if "." in order[j]:
                                order[j] = float(order[j])
                            else:
                                order[j] = 0
                        # 代码位数补齐至六位
                        if len(order[0]) < 6:
                            order[0] = "0" * (6 - len(order[0])) + order[0]
                        fund_list.append(order)

            except Exception as ex:
                logging.exception(str(ex))

        if "2、创建pandas数据表-----------------":
            title = ["代码", "名称", "英文", "日期", "单位净值", "累积净值", "日增长", "近1周", "近1月", "近3月", "近6月", "近1年", "近2年", "近3年",
                     "今年来", "成立来", "成立时间", "未知", "成立来2", "折前手续费", "手续费", "折数", "手续费2", "折数2", "未知2"]
            fund_df = pd.DataFrame(fund_list, columns=title)
            # 只取到成立时间（含）以前的属性
            fund_df = fund_df.iloc[:, :17]
            # 按照代码升序调整
            fund_df = fund_df.sort_values(by='代码', axis=0, ascending=True).reset_index(drop=True)
            # 保留第一次出现的那条数据
            fund_df = fund_df.drop_duplicates(keep='first')

        if "3、保存到文件 ":
            file = u'data/wholeInfo.xlsx'
            fund_df.to_excel(file, index=False, encoding='gbk')
            return fund_df

    # if 1:
    #     df = crawl_whole_info_table()
    #     print(df)

if "抓取一个基金的历史价格 --------------------------------":
    def crawl_one_fund_price(code, per=49, sdate='', edate=''):
        """
        一页最多爬 49 个记录 如果设置为 50，只会显示 20 条
        :param code: 一个基金的代码
        :param per: 一页返回 per 条数据
        :param sdate: 开始日期
        :param edate: 结束日期
        :return: void
        """
        if "1、获取总页数和表头 ---------------":
            """
            eg: https://fundf10.eastmoney.com/F10DataApi.aspx?type=lsjz&code=002939&page=1&per=48&sdate=&edate=
            页面样例如下：
            var apidata={ content:"
                净值日期	单位净值	累计净值	日增长率	申购状态	赎回状态	分红送配
                2022-02-11	2.9713	3.0163	-2.14%	开放申购	开放赎回	
                ......
                ",records:1313,pages:28,curpage:1};
            """
            url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx'
            params = {'type': 'lsjz', 'code': code, 'page': 1, 'per': per, 'sdate': sdate, 'edate': edate}
            rsp = requests.get(url, params)
            rsp.raise_for_status()
            html = rsp.text
            # 使用正则表达式读取总页数 pages
            pattern = re.compile(r'pages:(.*),')
            pages = int(re.search(pattern, html).group(1))
            """
            表头样式源代码
            <tr>
                <th class="first">净值日期</th>
                <th>单位净值</th>
                ...
                <th class="tor last">分红送配</th>
            </tr>
            """
            heads = []
            soup = BeautifulSoup(html, 'html.parser')
            for head in soup.findAll("th"):
                heads.append(head.contents[0])

        if "2、开始抓取 -----------------":
            records = []
            page = 1
            while page <= pages:
                params = {'type': 'lsjz', 'code': code, 'page': page, 'per': per, 'sdate': sdate, 'edate': edate}
                rsp = requests.get(url, params=params)
                rsp.raise_for_status()
                html = rsp.text
                soup = BeautifulSoup(html, 'html.parser')
                """
                基金数据表格样式源代码
                <tbody>
                    <tr>
                        <td>2022-02-11</td>
                        <td class="tor bold">2.9713</td>
                        <td class="tor bold">3.0163</td>
                        <td class="tor bold grn">-2.14%</td>
                        <td>开放申购</td>
                        <td>开放赎回</td>
                        <td class="red unbold"></td>
                    </tr>
                    <tr>
                    ...
                    </tr>
                    ...
                </tbody>
                """
                for row in soup.findAll("tbody")[0].findAll("tr"):
                    row_records = []
                    for record in row.findAll('td'):
                        val = record.contents
                        # 处理空值
                        if not val:
                            row_records.append(np.nan)
                        else:
                            row_records.append(val[0])
                    records.append(row_records)
                page = page + 1

            if len(records) == 0:
                records = [[np.nan, np.nan, np.nan, np.nan, np.nan, "---", "---", np.nan]]
        if "3、得到数据表 ---------------":
            np_records = np.array(records)
            data = pd.DataFrame()
            for col, col_name in enumerate(heads):
                data[col_name] = np_records[:, col]

            data['单位净值'] = data['单位净值'].astype(float)
            data['累计净值'] = data['累计净值'].astype(float)
            data['日增长率'] = data['日增长率'].str.strip('%').astype(float)
            data = data.sort_values(by='净值日期', axis=0, ascending=True).reset_index(drop=True)
        if "4、保存到文件 ":
            file = u'data_new/{}_new.xlsx'.format(code)
            data.to_excel(file, index=False, encoding='gbk')

    # if 1:
    #     file = u"data/wholeInfo.xlsx"
    #     df = pd.read_excel(file, usecols=['代码'], dtype={'代码': str})
    #     total = len(df)
    #     count = 0
    #     start = datetime.datetime.now()
    #     wrong_list = []
    #
    #     # 读取各个基金信息，同时对每条信息计算所消耗的时间，进行格式化输出
    #     for i in range(100):
    #         count += 1
    #         if not os.path.exists("data_new/" + df.iloc[i, 0] + '_new.xlsx'):
    #             this_start = datetime.datetime.now()
    #             try:
    #                 crawl_one_fund_price(df.iloc[i, 0])
    #                 this_end = datetime.datetime.now()
    #                 print("Done [{}]. ({:5} / {:5}) items finished.  ({} / {}) items used time.".
    #                       format(df.iloc[i, 0], count, total, this_end - this_start, this_end - start))
    #             # 防止因为出错而中断了程序
    #             except requests.exceptions.Timeout or requests.exceptions.ConnectionError:
    #                 print("wrong [{}]. test again later.".format(df.iloc[i, 0]))
    #                 wrong_list.append(df.iloc[i, 0])
    #                 sleep(10)
    #                 continue
    #         else:
    #             print("exists [{}]. ({:5} / {:5}) items finished.".format(df.iloc[i - 1, 0], count, total))
    #     print(wrong_list, "should crawl again.")

if "数据表的窗口可视化------------------------":
    def treeview_dataframe_general(df, table_info=""):
        """
        :param df: dataframe 格式的表格
        :param table_info: 标题
        :return: none 直接显示界面
        """
        if "窗口基本属性 -------------":
            min_num = 29 if len(df) > 29 else len(df)
            win_width = len(df.columns) * 110 + 100
            win_width = 1300 if win_width > 1300 else win_width
            win_high = len(df) * 20 + 100
            win_high = 600 if win_high > 600 else win_high

            win = tk.Tk()
            win.geometry(str(win_width + 100) + "x" + str(win_high + 100))
            win.title(table_info)
            win.resizable(width=True, height=True)

            tk.Label(win, text=table_info + " 共" + str(len(df)) + "行", font=('微软雅黑', 14), width=60,
                     height=2).pack()

        if "创建表格窗体 -------------":
            tree = ttk.Treeview(win, height=min_num, show="tree headings")

            # "增加滚动条":
            vsb = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
            vsb.pack(side='right', fill='y')
            tree.configure(yscrollcommand=vsb.set)

        if "表格行列添加 -------------":
            # 列设置
            tree["columns"] = tuple(["index"] + list(df.columns))
            tree.column("#0", width=0, anchor="center")
            tree.column("index", width=50, anchor="center")

            column_width = int((win_width - 50) / len(df.columns))
            for col in df.columns:  # 增加列
                if col == '代码':
                    tree.column(col, width=50, anchor="center")
                else:
                    tree.column(col, width=column_width, anchor="center")
                tree.heading(col, text=col, anchor="center")

            # 行设置
            for x in range(len(df)):  # 增加行
                item = [list(df.index)[x]]
                for col in df.columns:
                    item.append(df.iloc[x][col])
                tree.insert("", x, text=str(x + 1), values=item)

            tree.pack()
            win.mainloop()

    # if 1:
    #     Dataset = crawl_whole_info_table()
    #     treeview_dataframe_general(Dataset)

if "读取data文件夹基金价格文件-----------":
    def read_filenames_from_folder(folder):
        filename_list = []
        for root, dirs, files in os.walk(folder):
            for f in files:
                portion = os.path.splitext(f)
                if portion[1] == ".xlsx" and len(portion[0]) == 6:
                    filename_list.append(portion[0])
        return filename_list

    # if 1:
    #     all_codes = read_filenames_from_folder("data")  # 这条语句可以读取并返回data文件夹下的所有基金代码
    #     print("基金个数", len(all_codes))
    #     print(all_codes)

if "基金历史价格可视化------------------------":
    # 知识点：循环、文件读取、函数、pandas、matplotlib
    def figure_fund_price_history(codes, start_day="1000-01-01", end_day="3000-01-01"):  # 重要
        if "读取基金价格--------------------------------":
            codes_dict = {}
            for code in codes:
                start = start_day
                end = end_day
                df = pd.read_excel(u"data/" + code + '.xlsx')
                df = df.reindex(columns=["净值日期", "单位净值", "日增长率", "累计净值"])

                if df.iloc[0, 0] > start_day:
                    start = df.iloc[0, 0]
                if df.iloc[len(df) - 1, 0] < end_day:
                    end = df.iloc[len(df) - 1, 0]

                df = (df[np.array(df['净值日期'] >= start) & np.array(df['净值日期'] <= end)]).copy()
                df['净值日期'] = pd.to_datetime(df['净值日期'], format='%Y-%m-%d')
                codes_dict[code] = df

        if "画图---------------------------------------":
            plt.figure(figsize=(16, 8), dpi=150)
            plt.rcParams['font.family'] = 'Microsoft YaHei'
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

            plt.title('基金：' + ' '.join(codes) + '  价格历史行情')
            plt.xlabel('时间')
            plt.ylabel('价格')
            plt.grid(True)

            color = ["m", "g", "b", "c", "y", "r"]
            style = ["-", "--", ":", "-."]
            line_style = []
            for s in style:
                for c in color:
                    line_style.append(c + s)
            random.shuffle(line_style)  # 随机打乱

            i = 0
            for code in codes:
                plt.plot_date(codes_dict[code]["净值日期"], codes_dict[code]["单位净值"], line_style[i], label=code)
                i = i + 1

            plt.legend(numpoints=1, fontsize=14)
            plt.legend(loc='upper left')
            plt.savefig('./src/price_trend.jpg')
            plt.show()

    # if 1:
    #     all_codes = read_filenames_from_folder("data")
    #     codes = all_codes[:5]
    #     figure_fund_price_history(codes, start_day="1980-01-01", end_day="2020-01-01")

if "基金价格涨跌日比率计算-----------------":
    def fund_rise_days_num(codes, start_day="1000-01-01", end_day="3000-01-01"):
        ratio = []
        count = 0
        total = len(codes)
        for code in codes:
            start = start_day
            end = end_day
            count += 1

            file = u"data/" + code + '.xlsx'  # 由crawl_fund_price.py 抓取
            if not os.path.exists(file):
                return "not exist"

            df = pd.read_excel(file, usecols=["净值日期", "单位净值", "日增长率"])

            if isinstance(df.iloc[0, 0], float):
                print('\n', code, ' has a wrong start day, so ignore.')
                continue

            if df.iloc[0, 0] > start_day:
                start = df.iloc[0, 0]
            if df.iloc[len(df) - 1, 0] < end_day:
                end = df.iloc[len(df) - 1, 0]

            df = (df[np.array(df['净值日期'] >= start) & np.array(df['净值日期'] <= end)]).copy()
            df['净值日期'] = pd.to_datetime(df['净值日期'], format='%Y-%m-%d')

            df = df[df["单位净值"] != ""]  # 删除没有值的行
            all_days_num = df.shape[0]
            if all_days_num == 0:
                print('\n', code, ' has no any valid day data, so ignore.')
                continue

            df_rise = df[df["日增长率"] > 0]
            rise_days_num = df_rise.shape[0]
            rise_ratio = round(rise_days_num / all_days_num, 4)

            df_down = df[df["日增长率"] < 0]
            down_days_num = df_down.shape[0]
            down_ratio = round(down_days_num / all_days_num, 4)

            ratio.append([code, rise_ratio, down_ratio])

            print("\rDone [{}]. ({:5} / {:5}) items finished.".format(code, count, total), end='')

        print("")
        np_ratio = np.array(ratio)
        df_ratio = pd.DataFrame()
        df_ratio['code'] = np_ratio[:, 0]
        df_ratio['rise'] = np_ratio[:, 1]
        df_ratio['down'] = np_ratio[:, 2]
        df_ratio['rise'] = df_ratio['rise'].astype(float)
        df_ratio['down'] = df_ratio['down'].astype(float)
        return df_ratio

    # if 1:
    #     selected_codes = read_filenames_from_folder("data")[0:3]
    #     df = fund_rise_days_num(selected_codes)
    #     print(df)

if "近一个月来情况价格-----------------------":
    def recent_price(code):
        file = u"data/" + code + '.xlsx'
        if not os.path.exists(file):
            return "not exist"

        df = pd.read_excel(file)
        df = df[df["单位净值"] != ""]  # 删除没有值的行
        df = df[df["净值日期"] > "2021-01-16"]  # 删除没有值的行
        return df

    # if 1:
    #     df = recent_price("002939")
    #     print(df.shape, df.shape[0], df.shape[1])
    #     treeview_dataframe_general(df, "002939 近一个月来情况价格")

if "作业A.1-------------------------------":
    # 编写函数，输出基金名字中包含有“混合”
    # 两字的基金名称及其代码（从总简表中）；
    def homework_A_1():
        file = u"data/wholeInfo.xlsx"
        if not os.path.exists(file):
            return "not exist"
        df = pd.read_excel(file, usecols=['代码', '名称'], dtype={'代码': str})
        return df[df['名称'].str.contains('混合')]

    # if 1:
    #     homework_a1 = homework_A_1()
    #     treeview_dataframe_general(homework_a1, "作业A.1")

if "作业A.2-------------------------------":
    # 编写函数，输出所有基金名称的云图（从总简表中）；
    def homework_A_2():
        background = plt.imread('src/beijing.jpeg')
        file = u"data/wholeInfo.xlsx"
        if not os.path.exists(file):
            return "not exist"
        df = pd.read_excel(file, usecols=['名称'])
        text = ','.join([x[0] for x in df.values.tolist()])

        wordcloud = WordCloud(
            background_color="white",
            max_words=1000,
            mask=background,
            font_path='src/font.TTF')
        wordcloud.generate(text)
        wordcloud.to_file("src/wordcloud.png")

        plt.figure()
        plt.axis('off')
        plt.imshow(wordcloud)
        plt.show()

    # if 1:
    #     homework_A_2()

if "作业A.3-------------------------------":
    # 编写函数，输出跌天数比率最大的 10 个基金的代码（从价格文件中）；
    def homework_A_3():
        selected_codes = read_filenames_from_folder("data")
        df = fund_rise_days_num(selected_codes)
        df.sort_values(by=['down'], ascending=False, inplace=True)
        return df.values.tolist()[:10]

    # if 1:
    #     homework_a3 = homework_A_3()
    #     count = 1
    #     for i in homework_a3:
    #         print("[{:2}] code: {}, down_ratio = {:.2%}".format(count, i[0], i[2]))
    #         count += 1

if "作业A.4-------------------------------":
    # 编写函数，可以画出多个基金的价格变化曲线（从价格文件中）；
    def homework_A_4():
        all_codes = read_filenames_from_folder("data")
        selected_codes = random.sample(all_codes, 10)
        figure_fund_price_history(selected_codes, start_day="2021-01-01", end_day="2022-01-01")

    # if 1:
    #     homework_A_4()

if "作业A.5-------------------------------":
    # 编写函数，输出近 1 个月来跌幅最大的 10 个基金（从总简表中）；
    def homework_A_5():
        file = u"data/wholeInfo.xlsx"
        if not os.path.exists(file):
            return "not exist"
        df = pd.read_excel(file, usecols=['代码', '近1月'], dtype={'代码': str, '近1月': float})
        df.sort_values(by=['近1月'], ascending=True, inplace=True)
        return df.values.tolist()[:10]

    # if 1:
    #     homework_a5 = homework_A_5()
    #     count = 1
    #     for i in homework_a5:
    #         print("[{:2}] code: {}, down_recent_1_month = {:.2f}%".format(count, i[0], i[1]))
    #         count += 1

if "作业A.6-------------------------------":
    # 编写函数，可实现对于指定的一些基金 codes，
    # 输出近一个月来涨的天数比率最大的 10 个基金的代码；
    def homework_A_6():
        # 如果是最新的这近一个月的，可以用下面的代码替换，datetime库来取最近30天的数据
        # codes = read_filenames_from_folder("data")[:20]
        # yesterday = (datetime.date.today() + datetime.timedelta(-1)).strftime("%Y-%m-%d")
        # one_month_before = (datetime.date.today() + datetime.timedelta(-31)).strftime("%Y-%m-%d")
        # df_ratio = fund_rise_days_num(codes, start_day=one_month_before, end_day=yesterday)
        # df_ratio.sort_values(by=['rise'], ascending=False, inplace=True)
        # return df_ratio.values.tolist()[:10]

        codes = read_filenames_from_folder("data")[:50]
        yesterday = "2021-11-26"
        one_month_before = "2021-10-26"
        df_ratio = fund_rise_days_num(codes, start_day=one_month_before, end_day=yesterday)
        df_ratio.sort_values(by=['rise'], ascending=False, inplace=True)
        return df_ratio.values.tolist()[:10]

    # if 1:
    #     homework_a6 = homework_A_6()
    #     count = 1
    #     for i in homework_a6:
    #         print("[{:2}] code: {}, rise_rate_recent_1_month = {:.2%}".format(count, i[0], i[1]))
    #         count += 1

if "作业A.7-------------------------------":
    # 编写函数，输出近 1 周来和近 1 个月来
    # 跌幅都排名在前 20 的基金（从总简表中）；
    def homework_A_7():
        file = u"data/wholeInfo.xlsx"
        if not os.path.exists(file):
            return "not exist"
        df = pd.read_excel(file, usecols=['代码', '近1月', '近1周'], dtype={'代码': str, '近1月': float, '近1周': float})
        df1 = df.sort_values(by=['近1月'], ascending=True)[:100]
        df2 = df.sort_values(by=['近1周'], ascending=True)[:100]
        return pd.merge(df1, df2)

    # if 1:
    #     homework_a7 = homework_A_7()
    #     if len(homework_a7) == 0:
    #         print("没有近 1 周来和近 1 个月来跌幅都排名在前 20 的基金！")
    #     else:
    #         print(homework_a7)

if "作业B.8-------------------------------":
    # 编写函数 rising_days_distribution(code)，可以统计某一个基金 code 的连续涨跌天数，
    # 并以直方图的形式画出其连续涨跌天数分布直方图（从价格文件中）；

    def rising_days_distribution(code):
        file = u"data/" + code + '.xlsx'
        if not os.path.exists(file):
            return "not exist"

        df = pd.read_excel(file, usecols=['单位净值'])

        i = 1
        count = 0
        rising_days_list = []
        while i < len(df):

            while i < len(df) and df.iloc[i, 0] > df.iloc[i - 1, 0]:
                count += 1
                i += 1
            if count > 0:
                rising_days_list.append(count)
                count = 0

            while i < len(df) and df.iloc[i, 0] < df.iloc[i - 1, 0]:
                count += 1
                i += 1
            if count > 0:
                rising_days_list.append(-count)
                count = 0

            while i < len(df) and df.iloc[i, 0] == df.iloc[i - 1, 0]:
                i += 1

        if len(rising_days_list) == 0:
            print(code, "has no any data please try again.")
            return

        max_num = max(rising_days_list)
        min_num = min(rising_days_list)

        plt.figure(figsize=(10, 5), dpi=150)
        plt.rcParams['font.family'] = 'Microsoft YaHei'
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

        bins = np.arange(min_num, max_num + 2) - 0.5
        nums, bins, patches = plt.hist(rising_days_list, color='steelblue', edgecolor='black', bins=bins)
        for bin, num in zip(bins, nums):
            plt.text(bin + 0.5, num, int(num), ha='center', va='bottom', fontsize=10)

        plt.title(code + ' 的连续涨跌天数')
        plt.xticks(range(min_num, max_num + 1))
        plt.xlim([min_num - 1, max_num + 1])
        plt.xlabel('连续天数（负数为连续下跌，整数为连续上涨）/天')
        plt.ylabel('频数/次')
        plt.savefig('./src/rise_down_trend.jpg')
        plt.show()


    if 1:
        code = random.choice(read_filenames_from_folder("data"))
        rising_days_distribution(code)

if "作业B.10-------------------------------":
    # 编写函数 gain_loss_max(codes, money, from_date, end_date),
    # 计算如果分别都投入资金数额为 money 的资金给代码为 codes 的多个基金
    # （codes 为基金代码序列），投资时间范围是从 from_date 到 end_date，
    # 计算投资哪支基金的收益将会最大，输出该基金代码、名称，及相应的收益额（从价格文件中）；

    def get_code_name(code):
        file = u"data/wholeInfo.xlsx"
        if not os.path.exists(file):
            return "not exist"
        df = pd.read_excel(file, usecols=['代码', '名称'], dtype={'代码': str})
        return df[df['代码'] == code].iloc[0, 1]

    def get_redemption_rate_and_price(code, from_date='1900-01-01', end_date='2100-01-01'):
        """
        根据交易日 delta 计算基金赎回费率与起始日期的累计净值
        :param code: 代码
        :param from_date: 开始日期
        :param end_date: 结束日期
        :return: 基金赎回费率
        """
        file = u"data/" + code + '.xlsx'
        if not os.path.exists(file):
            return "not exist"

        if from_date > end_date:
            from_date, end_date = end_date, from_date

        year, month, day = [int(x) for x in from_date.split('-')]
        time_1_struct = datetime.date(year, month, day)
        year, month, day = [int(x) for x in end_date.split('-')]
        time_2_struct = datetime.date(year, month, day)
        delta = (time_2_struct - time_1_struct).days

        if delta < 7:
            redemption_rate = 0.0150
        elif delta < 30:
            redemption_rate = 0.0075
        elif delta < 365:
            redemption_rate = 0.0050
        elif delta < 365 * 2:
            redemption_rate = 0.0025
        else:
            redemption_rate = 0

        df = pd.read_excel(file, usecols=["净值日期", "累计净值"])
        if df.iloc[0, 0] > from_date:
            from_date = df.iloc[0, 0]
        if df.iloc[len(df) - 1, 0] < end_date:
            end_date = df.iloc[len(df) - 1, 0]
        df = (df[np.array(df['净值日期'] >= from_date) & np.array(df['净值日期'] <= end_date)]).copy()

        from_price = df.iloc[0, 1]
        end_price = df.iloc[-1, 1]

        return redemption_rate, from_price, end_price


    def gain_loss(code, money=10000, from_date='1900-01-01', end_date='2100-01-01'):
        """
        计算从 from_date 天开始投入 money 元购买代码为 code 的基金，到 end_date 这一天的盈利或亏损
        :param code: 代码
        :param money: 金额
        :param from_date: 开始日期
        :param end_date: 结束日期
        :return: 盈亏金额
        """
        subscription_rate = 0.015
        redemption_rate, from_price, end_price = get_redemption_rate_and_price(code, from_date, end_date)

        net_subscription_money = money / (1 + subscription_rate)
        subscription_portion = net_subscription_money / from_price

        redemption_money = subscription_portion * end_price
        net_redemption_money = redemption_money * (1 - redemption_rate)
        return net_redemption_money - money


    def gain_loss_max(codes, money, from_date, end_date):
        gain_loss_dict = {}
        for code in codes:
            result = gain_loss(code, money, from_date, end_date)
            gain_loss_dict[code] = result
        return sorted(gain_loss_dict.items(), key=lambda x: x[1], reverse=True)[0]

    # if 1:
    #     all_codes = read_filenames_from_folder("data")
    #
    #     selected_codes = random.sample(all_codes, 10)
    #     print("you select codes are:")
    #     count = 0
    #     for code in selected_codes:
    #         count += 1
    #         print("[{:2}] [{}] {}".format(count, code, get_code_name(code)))
    #     money = 100000
    #     from_date = "2021-01-01"
    #     end_date = "2022-01-01"
    #     max_code, max_money = gain_loss_max(selected_codes, money, from_date, end_date)
    #     max_name = get_code_name(max_code)
    #     print("max is {}, code = {}, you can earn ￥{:.2f}.".format(max_name, max_code, max_money))

if "作业C.11-------------------------------":
    # 抓取主题基金：编写程序抓取各个主题或行业的基金代码。
    def get_codes(driver, theme_id):
        codes = []

        # 获得当前主题的页面数量 page_num, 查询条件是 "li[data-id='BKXXXX'] .num" class="num" 的最后一个，
        # 如果查询不到任何一个类为 num 的，就是只有一页，被选中的的页面类为 num on
        # 而且由于这个网页是内部自带像标签页的模式(热门主题、主题索引、交运设备套了一次，主题基金、相关股票又套一次)，
        # 首先还要在源代码中选中当前页签才行
        query_str = "div[class='tab-page'][data-tab='" + theme_id + "'] div[data-tab='zt'] .pagination-count"
        driver.implicitly_wait(10)
        page_num = driver.find_element(By.CSS_SELECTOR, query_str).text[1:-1]
        # 对当前主题每页进行提取
        for i in range(int(page_num)):
            print('\r[{}] finished {:2}/{:2} page(s).'.format(theme_id, i + 1, page_num), end='')
            # 获得当前主题的页面所有的 code 加入 codes
            driver.implicitly_wait(10)
            for code in driver.find_elements(By.CSS_SELECTOR, ".fcode"):
                codes.append(code.text)

            # 当前页面代码都保存进 codes 列表，现在跳转到下一页
            driver.implicitly_wait(10)
            driver.find_element(By.CSS_SELECTOR, ".next-page.page").click()

        # 所有代码都保存进 codes 列表，现在返回主题页面
        driver.implicitly_wait(10)
        driver.find_element(By.CSS_SELECTOR, "li[data-id='zt']").click()
        sleep(0.8)

        return codes


    def share_browser():
        field_dict = {}
        concept_dict = {}
        driver = webdriver.Edge('src/msedgedriver.exe')
        driver.implicitly_wait(10)
        driver.get(r'http://fund.eastmoney.com/ztjj/#!curr/zt-%E4%B8%BB%E9%A2%98%E7%B4%A2%E5%BC%95/fs/SON_1N/fst/desc')
        """
        主题页面主题展示相关源代码
        <li data-type="hy" class="">
            <div class="div-zt-category-title">行业</div>
            <div class="div-zt-category-content">
                <ul>
                    <li data-name="交运设备" data-id="BK0429" class="">
                        <a target="_self" data-id="BK0429">交运设备</a>
                    </li>
                    <li data-name="农牧饲渔" data-id="BK0433" class="">
                        <a target="_self" data-id="BK0433">农牧饲渔</a>
                    </li>
                </ul>
                <div class="clear"></div>
            </div>
        </li>
        """
        driver.implicitly_wait(10)
        fields = driver.find_elements(By.CSS_SELECTOR, "li[data-type='hy'] a[data-id^='BK']")
        count = 0
        for field in fields:
            count += 1
            field_id = field.get_attribute('data-id')
            field_name = field.text
            field.click()
            sleep(0.8)
            field_dict[field.text] = get_codes(driver, field_id)
            print(" [{:^8}] finished {:2}/{:2}.".format(field_name, count, len(fields)))

        f = open('src/fields.txt', 'w')
        for k, v in field_dict.items():
            print(k, v)
            f.write(k + ': ' + ' '.join(v)+ '\n')
        f.close()

        driver.implicitly_wait(10)
        concepts = driver.find_elements(By.CSS_SELECTOR, "li[data-type='gn'] a[data-id^='BK']")
        count = 0
        for concept in concepts:
            count += 1
            concept_id = concept.get_attribute('data-id')
            concept_name = concept.text
            concept.click()
            sleep(0.8)
            concept_dict[concept.text] = get_codes(driver, concept_id)
            print(" [{:^8}] finished {:2}/{:2}.".format(concept_name, count, len(fields)))

        f = open('src/concepts.txt', 'w')
        for k, v in concept_dict.items():
            print(k, v)
            f.write(k + ': ' + ' '.join(v) + '\n')
        f.close()

        driver.quit()

    if 1:
        share_browser()
