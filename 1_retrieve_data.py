import pandas as pd
import numpy as np
import akshare as ak
import tushare as ts

import time as time
from datetime import datetime,timedelta

######### I.Setting #########

### tushare api
pro = ts.pro_api('8dda511a93baabfcb8a07fe88ca4d629bc5257cef10fa744cc2a83e1')


### work directory
dir='./'

### 时间设置
start_dt='20200512'
end_dt='20230623'


######### II.获取指数相关数据 #########

### II.1 读取指数代码列表

index_list=pd.read_excel(dir+'index_list.xlsx')
index_codes=list(index_list['代码'])


### II.2 获取指数成分股

df_index_components=pd.DataFrame()

for i in index_codes:
    tmp=pro.index_weight(index_code=i)
    df_index_components=pd.concat([df_index_components,tmp])

df_index_components=pd.merge(df_index_components,index_list,left_on='index_code',right_on='代码',how='left')
del df_index_components['代码']

df_index_components.to_excel(dir+'index_components.xlsx',index=False)


### II.3 指数交易数据

try:
    df_index_trade_data=pd.read_csv(dir+'index_weekly_trade_data.csv',converters={'trade_date':str})
except:
    df_index_trade_data=pd.DataFrame()

for i in index_codes:
    tmp=pro.index_weekly(ts_code=i, start_date=start_dt, end_date=end_dt, fields='ts_code,trade_date,open,high,low,close,vol,amount')
    df_index_trade_data=pd.concat([df_index_trade_data,tmp])

for i in ['close','open','high','low','vol','amount']:
    df_index_trade_data[i]=df_index_trade_data[i].apply(lambda x:round(x,2))
    
df_index_trade_data.drop_duplicates().to_csv(dir+'index_weekly_trade_data.csv',index=False)


######### III.获取股票相关数据 #########


### III.1 获取每日指标

df_index_components=pd.read_excel(dir+'index_components.xlsx')
con_list=sorted(list(set(df_index_components['con_code'])))


df_daily_metrics=pd.DataFrame()

for i in range(0,len(con_list),50):
    j=i+50
    for k in con_list[i:j]:
        tmp=pro.query('daily_basic',ts_code=k,start_date=start_dt,end_date=end_dt)
        df_daily_metrics=pd.concat([df_daily_metrics,tmp])
    time.sleep(10)


df_daily_metrics['trade_date2']=pd.to_datetime(df_daily_metrics['trade_date'])
df_daily_metrics['trade_week']=df_daily_metrics['trade_date2'].apply(lambda x:x.isocalendar().week)
df_daily_metrics['trade_month']=df_daily_metrics['trade_date2'].apply(lambda x:x.month)
df_daily_metrics['trade_year']=df_daily_metrics['trade_date2'].apply(lambda x:x.isocalendar().year)

del df_daily_metrics['trade_date2']


df_daily_metrics_total=pd.read_csv(dir+'stock_daily_metric.csv',converters={'trade_date':str})
df_daily_metrics_total=pd.concat([df_daily_metrics_total,df_daily_metrics])
df_daily_metrics_total['total_mv']=df_daily_metrics_total['total_mv'].apply(lambda x:round(x,2))
df_daily_metrics_total['circ_mv']=df_daily_metrics_total['circ_mv'].apply(lambda x:round(x,2))

df_daily_metrics_total.drop_duplicates().to_csv(dir+'stock_daily_metric.csv',index=False)

### III.2 获取股票基础信息

df_stock_basic= pro.stock_basic(exchange='',fields='ts_code,symbol,name,area,industry,list_date')
df_stock_basic.drop_duplicates().to_csv(dir+'stock_basic.csv',index=False)


### III.3 获取财务数据
df_stock_earning=pd.DataFrame()

for i in range(0,len(con_list),50):
    print(i)
    j=i+50
    for k in con_list[i:j]:
        tmp=pro.income(ts_code=k,start_date=start_dt,end_date=end_dt,fields='ts_code,ann_date,end_date,total_profit,n_income,n_income_attr_p')
        df=pd.concat([df,tmp]).drop_duplicates().reset_index(drop=True)
    time.sleep(30)

df_stock_earning.to_csv(dir + 'stock_earning.csv',index=False)

df_stock_bs=pd.DataFrame()

for i in range(0,len(con_list),50):
    print(i)
    j=i+50
    for k in con_list[i:j]:
        tmp=pro.balancesheet(ts_code=k,start_date=start_dt,end_date=end_dt)
        df=pd.concat([df,tmp]).drop_duplicates().reset_index(drop=True)
    time.sleep(30)

df_stock_bs.to_csv(dir + 'stock_balancesheet.csv',index=False)



######### IV.获取基金数据 #########

### IV.1 公募基金列表
today = datetime.today()
dt_L1Yr=(today + timedelta(days=-360)).strftime('%Y%m%d')

df_fund_list=pro.fund_basic(market='O')
df_fund_list['C_flg']=df_fund_list['name'].apply(lambda x:1 if x[-1]=='C' else 0)
df_fund_list=df_fund_list[(df_fund_list['fund_type'].isin(['混合型', '股票型']))&(df_fund_list['status']!='D')&(df_fund_list['issue_date']<=dt_L1Yr)&(df_fund_list['C_flg']!=1)].rename(columns={'name':'fund_name'}).reset_index(drop=True)

df_fund_list.to_csv(dir+'fund_name_list.csv',index=False)

df_fund_list.shape


### IV.2 基金持仓 -- 季度更新
df_fund_list=pd.read_csv(dir+'fund_name_list.csv')
fund_list=list(df_fund_list['ts_code'])

try:
    df_fund_holdings=pd.read_csv(dir+'fund_holdings.csv',converters={'ann_date':str,'end_date':str})
except:
    df_fund_holdings=pd.DataFrame()

for i in range(0,len(fund_list),20):
    print(i)
    j=i+20
    for k in fund_list[i:j]:
        tmp=pro.fund_portfolio(ts_code=k,start_date='20221201')
        df_fund_holdings=pd.concat([df_fund_holdings,tmp]).drop_duplicates().reset_index(drop=True)
    time.sleep(30)
    
df_fund_holdings.to_csv(dir+'fund_holdings.csv',index=False)


### IV.3 基金净值规模 -- 季度更新

try:
    df_fund_nav=pd.read_csv(dir+'fund_nav.csv',converters={'ann_date':str,'nav_date':str})
except:
    df_fund_nav=pd.DataFrame()

for i in range(0,len(fund_list),20):
    print(i)
    j=i+20
    for k in fund_list[i:j]:
        tmp=pro.fund_nav(ts_code=k,start_date='20221201')
        df_fund_nav=pd.concat([df_fund_nav,tmp[tmp['total_netasset'].isna()==False]]).reset_index(drop=True)
    time.sleep(30)
    
df_fund_nav.to_csv(dir+'fund_nav.csv',index=False)



