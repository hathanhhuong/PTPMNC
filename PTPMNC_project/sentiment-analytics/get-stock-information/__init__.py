import logging
from datetime import datetime , timezone , timedelta
import azure.functions as func
from azure.cosmos import  CosmosClient
import json
import os
import re
from pandasql import sqldf
import pandas as pd
import math
url =os.environ['URL']
key=os.environ['KEY']
container_name='stock_label'
db='sa'


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    logging.info(url+'   '+key)
    try:
        username = req.headers['username']
        password = req.headers['password']
    except:
        return func.HttpResponse(json.dumps({'status_code' : "200",
                                         'status' : f"username/password is blank",
                                         "totalPage" :"",
                                         'data': [],
                                         "page" : "",
                                         "pageSize": ""}
                                          ))  
        # return func.HttpResponse("Nhập vào username và password")
    if username != "DS2023" or password != "4A3E68AC":
        return func.HttpResponse(json.dumps({'status_code' : "200",
                                         'status' : f"username/password is wrong",
                                         "totalPage" : "",
                                         'data': [],
                                         "page" : "",
                                         "pageSize": ""}
                                          ))
        # return func.HttpResponse("Sai username hoặc password")
    stock_code  = req.params.get('stock_code')
    from_date        = req.params.get('from_date')
    page = int(req.params['page'])
    pageSize = int(req.params['pageSize'])
    today=datetime.now(tz=timezone(timedelta(hours=7))).strftime('%Y-%m-%d')
    try:
        to_date = req.params['to_date']

    except Exception as e:
        logging.info('Fault '+ str(e))
        logging.info('No to_date')
        to_date = today

    try:
        label = req.params['label'].lower()
        label = f" and r.label = '{label}'"
    except Exception as e:
        logging.info('Fault '+ str(e))
        logging.info('No label')
        label = ''

    query = f"where r.stock_code = '{stock_code}' and r.created_date >= '{from_date}' and r.created_date <= '{to_date}' " +label
    #get Active survey 
    client = CosmosClient(url=url,credential=key)
    database = client.get_database_client(db)
    container  = database.get_container_client(container=container_name)

    items = list(container.query_items(
        query=f"SELECT * FROM r {query} \
                order by r.created_date desc ",
        enable_cross_partition_query=True
    ))

    logging.info(f"SELECT * FROM r {query} order by r.created_date desc ")
    
    if len(items) == 0:
        return func.HttpResponse(json.dumps({'status_code' : "200",
                                         'status' : f"No information of {stock_code} between {from_date} and {to_date}",
                                         "totalPage" : "",
                                         'data': [],
                                         "page" : "",
                                         "pageSize": ""}
                                          )) 
    res = []
    
    for i in items:
        stock_code = i['stock_code']
        content = i['content']
        article = i['article']
        created_date =  i['created_date']
        label = i['label']
        res.append({
            "stock_code" : stock_code,
            "content" : content,
            "article" : article,
            "created_date" : created_date,
            "label": label
        })
    totalPage = math.ceil(len(res)/pageSize)
    logging.info(totalPage)
    if page == totalPage:
        data = res[(page-1)*pageSize:]
    else:
        data = res[(page-1)*pageSize: page*pageSize-1]
    return func.HttpResponse(json.dumps({'status_code' : "200",
                                         'status' : "Get data successfully",
                                         "totalPage" : str(totalPage),
                                         'data': data,
                                         "page" : page,
                                         "pageSize": pageSize}
                                          ))
 