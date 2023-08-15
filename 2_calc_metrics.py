import pandas as pd
import numpy as np
import tushare as ts

import time as time
from datetime import datetime,timedelta

######### I.Setting #########

### I.1 work directory
dir='./'

### I.2 read data
index_list=pd.read_excel(dir+'index_list.xlsx')
index_list=list(set(index_list['代码']))
df_index_components=pd.read_excel(dir+'index_components.xlsx',converters={'trade_date':str}).rename(columns={'trade_date':'weight_dt'})
df_index_trade_data=pd.read_csv(dir+'index_weekly_trade_data.csv',converters={'trade_date':str})

df_daily_metric=pd.read_csv(dir+'stock_daily_metric.csv',converters={'trade_date':str}).drop_duplicates()
df_stock_basic=pd.read_csv(dir+'stock_basic.csv').drop_duplicates()

df_fund_list=pd.read_csv(dir+'fund_name_list.csv').drop_duplicates()
df_fund_holdings=pd.read_csv(dir+'fund_holdings.csv',converters={'ann_date':str,'end_date':str}).drop_duplicates()
df_fund_nav=pd.read_csv(dir+'fund_nav.csv',converters={'nav_date':str}).drop_duplicates()


######### II.指数指标计算 #########


### II.1 指数成分股

df_index_components['weight_dt2']=pd.to_datetime(df_index_components['weight_dt'])+pd.offsets.DateOffset(months=1)
df_index_components['month']=df_index_components['weight_dt2'].apply(lambda x:x.month)
df_index_components['year']=df_index_components['weight_dt2'].apply(lambda x:x.year)

del df_index_components['weight_dt2']


### II.2 股票每日指标只保留每周最后一条记录
df_daily_metric['week_rank']=df_daily_metric.groupby(['ts_code','trade_year','trade_week'])['trade_date'].rank(ascending=False,method='first')
df_weekly_metric=df_daily_metric[df_daily_metric['week_rank']==1].reset_index(drop=True)
df_weekly_metric=pd.merge(df_weekly_metric,df_stock_basic[['ts_code','name']],on='ts_code').rename(columns={'trade_date':'trade_date_v0'})

tmp=df_daily_metric.groupby(['trade_year','trade_week'])['trade_date'].max().reset_index()
df_weekly_metric=pd.merge(tmp,df_weekly_metric,on=['trade_year','trade_week'],how='left')

del df_weekly_metric['week_rank']

### II.3 通过股票获得指数的指标
df_weekly_metric_2=pd.DataFrame()

for i in index_list:
    tmp_index=df_index_components.loc[df_index_components['index_code']==i,['index_code','con_code','名称','year','month','weight']].rename(columns={'weight':'weight_0'})
    tmp=pd.merge(tmp_index,df_weekly_metric,left_on=['con_code','year','month'],right_on=['ts_code','trade_year','trade_month'])
    df_weekly_metric_2=pd.concat([df_weekly_metric_2,tmp])

df_weekly_metric_2['total_earnings']=df_weekly_metric_2['total_mv']/df_weekly_metric_2['pe']
df_weekly_metric_2['total_earnings_ttm']=df_weekly_metric_2['total_mv']/df_weekly_metric_2['pe_ttm']
df_weekly_metric_2['total_book_value']=df_weekly_metric_2['total_mv']/df_weekly_metric_2['pb']

del df_weekly_metric_2['trade_date_v0'],df_weekly_metric_2['weight_0']

df_weekly_metric_2.to_csv(dir+'stock_weekly_metric.csv',index=False)

df_weekly_metric_index=df_weekly_metric_2.groupby(['index_code','名称','trade_year','trade_week']).agg({'trade_date':'max','total_mv':'sum','total_earnings':'sum','total_earnings_ttm':'sum','total_book_value':'sum'}).reset_index()
df_weekly_metric_index['pe']=df_weekly_metric_index['total_mv']/df_weekly_metric_index['total_earnings']
df_weekly_metric_index['pb']=df_weekly_metric_index['total_mv']/df_weekly_metric_index['total_book_value']
df_weekly_metric_index['pe_ttm']=df_weekly_metric_index['total_mv']/df_weekly_metric_index['total_earnings_ttm']

df_weekly_metric_index=pd.merge(df_weekly_metric_index,df_index_trade_data,left_on=['index_code','trade_date'],right_on=['ts_code','trade_date'])

df_weekly_metric_index.to_csv(dir+'index_weekly_metric.csv',index=False)


######### III.基金推荐 #########

### III.1 获得基金成分
df_fund_holdings_2=pd.merge(df_fund_holdings,df_fund_nav[['ts_code','nav_date','unit_nav','accum_div','net_asset','total_netasset']],left_on=['ts_code','end_date'],right_on=['ts_code','nav_date'])
df_fund_holdings_2['stock_mkv_pct']=df_fund_holdings_2['mkv']/df_fund_holdings_2['total_netasset']

df_fund_holdings_2=pd.merge(df_fund_holdings_2,df_fund_list[['ts_code','fund_name','fund_type']],on='ts_code')
df_fund_holdings_2['year']=pd.to_datetime(df_fund_holdings_2['end_date']).apply(lambda x:x.year)
df_fund_holdings_2['month']=pd.to_datetime(df_fund_holdings_2['end_date']).apply(lambda x:x.month)

df_fund_index_pct=pd.DataFrame()

for i in index_list:
    tmp=df_index_components[df_index_components['index_code']==i]
    tmp_2=pd.merge(df_fund_holdings_2,tmp,left_on=['symbol','year','month'],right_on=['con_code','year','month'])
    tmp_3=pd.pivot_table(tmp_2,index=['ts_code','year','month','fund_name'],columns='名称',values='stock_mkv_pct',aggfunc='sum')

    df_fund_index_pct=pd.concat([df_fund_index_pct,tmp_3],axis=1).fillna(0)

### III.2 保留月末记录
df_fund_index_pct=df_fund_index_pct.reset_index()
df_fund_index_pct['yearmth']=df_fund_index_pct['year'].astype(int)*100+df_fund_index_pct['month'].astype(int)
df_fund_index_pct['rank']=df_fund_index_pct.groupby(['ts_code'])['yearmth'].rank(ascending=False)
df_fund_index_pct=df_fund_index_pct[df_fund_index_pct['rank']==1].reset_index(drop=True)
del df_fund_index_pct['rank']

df_fund_index_pct.to_csv(dir+'fund_index_pct.csv',index=False)






