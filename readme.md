## I.Background:

本程序旨在根据用户给定的需要进行统计的指数，给出该指数各指标与对应分位数的整体统计；并提供指数的具体指标的可视化分析，指定指数、指标与起始日期后绘制指数曲线与对应股票的曲线与其占比示意图；通关计算不同基金


## II.Steps:
**1. retrieve data 取数**

   通过tushare接口获取股票的交易和财务数据，指数的成分股，基金的净值和持仓数据
  **input files:**
  i) index_list.xlsx : 关注的指数列表
  ii) fund_name_list.csv : 关注的基金列表

  **output files:**
  i) index_components.xlsx： 关注指数的成分股
  ii) index_weekly_trade_data.csv: 指数周交易数据
