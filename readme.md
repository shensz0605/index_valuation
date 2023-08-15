## I.Background:

本程序旨在根据用户给定的需要进行统计的指数，给出该指数各指标与对应分位数的整体统计；并提供指数的具体指标的可视化分析，指定指数、指标与起始日期后绘制指数曲线与对应股票的曲线与其占比示意图；通关计算不同基金


## II.Steps:
### 1. retrieve_data 取数

   通过tushare接口获取股票的交易和财务数据，指数的成分股，基金的净值和持仓数据.  
  **input files:**  
  i) index_list.xlsx : 关注指数列表  

  **output files:**  
  i) index_components.xlsx： 关注指数的成分股  
  ii) index_weekly_trade_data.csv: 指数周交易数据  
  iii) stock_daily_metric.csv: 股票日指标    
  iv) stock_basic.csv: 股票基础信息  
  v) stock_earning.csv： 股票盈利数据  
  vi) stock_balancesheet.csv：股票资产负债表数据  
  vii) fund_name_list.csv : 基金列表  
  viii) fund_holdings.csv: 基金持仓数据  
  ix) fund_nav.csv: 基金净值数据  

### 2. calc_metrics 指标计算  
计算stock，index level的估值指标  
**input files:**  
i) index_list.xlsx: 关注指数列表  
ii) index_components.xlsx: 关注指数的成分股  
iii) index_weekly_trade_data.csv: 指数周交易数据  
iv) stock_daily_metric.csv: 股票日指标  
v) stock_basic.csv: 股票基础信息  
vi) fund_name_list.csv: 基金列表  
vii) fund_holdings.csv: 基金持仓数据  
viii) fund_nav.csv:  基金净值数据
