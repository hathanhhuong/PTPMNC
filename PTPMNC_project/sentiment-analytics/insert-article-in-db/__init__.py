import logging
import uuid
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey, exceptions
import json
import os
from datetime import datetime, timezone, timedelta
from azure.storage.blob import BlobServiceClient
import hashlib
url = os.environ['URL']
key = os.environ['KEY']
client = CosmosClient(url, credential=key)
database = client.get_database_client("sa")
container = database.get_container_client("articles")
storge_connect_str = os.environ['CONNECT_STR']
def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        username = req.headers['username']
        password = req.headers['password']
    except:
        return func.HttpResponse(json.dumps({"message": "username/password is blank",'status_code':'401'})) 
    if username != "DS2023" or password != "4A3E68AC":
        return func.HttpResponse(json.dumps({"message": "username/password is wrong",'status_code':'401'}))        
    try:
                
        logging.info('Python HTTP trigger function processed a request.')
        req_body = req.get_json()
        list_data = []
        for item in req_body:
            id = hashlib.md5(item.get('id').encode()).hexdigest()
            article = item.get('article')
            content = item['content']
            created_date = item['created_date']
            try:
                    tf  = datetime.strptime(created_date,"%Y-%m-%d")
            except:
                    # return func.HttpResponse("Nhập sai định dạng created_date, nhập vào dạng yyyy-mm-dd ")
                    return func.HttpResponse(json.dumps({"message": "Format date is wrong",'status_code':'500'})) 
            data = {"id": id, "article": article, "content": content,
            "created_date": created_date}
            list_data.append(data)        
            try:
                    container.upsert_item(data)
            except Exception as e:
                    logging.info(e)
                    return func.HttpResponse(json.dumps({"message": "Update failed",'status_code':'400'}))
        
         # save in datalake  
        # Lưu dữ liệu vào tệp JSON
        response_json_data = json.dumps(list_data)
        container_name = "hr-source"      
        blob_service_client = BlobServiceClient.from_connection_string(storge_connect_str)
        blob_client =blob_service_client.get_blob_client(container=container_name, blob = f"sa/" + "du_lieu.json")
        blob_client.upload_blob(response_json_data,overwrite=True)
        return func.HttpResponse(json.dumps({"message": "Done",'status_code':'200'}))
    except Exception as e:
        logging.info(e)
        return func.HttpResponse(json.dumps({"message": "Internal server error",'status_code':'500'}))
    

