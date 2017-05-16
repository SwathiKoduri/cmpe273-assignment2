from __future__ import print_function

import boto3
import json


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    
    dynamodb = boto3.resource('dynamodb', region_name='us-west-1', endpoint_url="https://dynamodb.us-west-1.amazonaws.com")


    table = dynamodb.Table('PizzaMenus')
    
    httpMethod = event.get('httpMethod')
    data = event.get('data')

    if httpMethod == "POST":    
        try:
            response = table.put_item(
               Item={
                    "menu_id":data["menu_id"],
                    "store_name" : data["store_name"],
                    "selection" : data["selection"],
                    "size" : data["size"],
                    "price" : data["price"],
                    "store_hours" : data["store_hours"]
                }
            )
        except:
            return "Invalid POST Request 400"
        else:
            return "200 OK"
    elif httpMethod == "GET":
        try:
            response = table.get_item(
                Key={"menu_id":event.get('param').get("menu_id")}
            )
        except:
            return "Invalid GET Request 400"
        else:
            return response['Item']
    elif httpMethod == "PUT":
        get_resp = table.get_item(
                Key={"menu_id":event.get('param').get("menu_id")}
            )
        existing_data = get_resp['Item']
        
        if event.get("store_name") == "":
            new_store_name = existing_data["store_name"]
        else:
            new_store_name = event.get("store_name")
        if len(event.get("size")) > 0:
            new_size = event.get("size")
        else:
            new_size = existing_data["size"]
        if len(event.get("selection")) > 0:
            new_selection = event.get("selection")
        else:
            new_selection = existing_data["selection"]
        if len(event.get("price")) > 0:
            new_price = event.get("price")
        else:
            new_price = existing_data["price"]
        if event.get("store_hours") == "":
            new_store_hours = existing_data["store_hours"]
        else:
            new_store_hours = event.get("store_hours")

        response = table.update_item(
            Key={
                "menu_id":event.get('param').get("menu_id")
            },
            UpdateExpression="set store_name = :sn, selection=:s, size=:sz, price=:p, store_hours=:sh",
            ExpressionAttributeValues={
                ':sn': new_store_name,
                ':s': new_selection,
                ':sz': new_size,
                ':p': new_price,
                ':sh': new_store_hours
            },
            ReturnValues="UPDATED_NEW"
        )
        print("size :")
        print(event.get("size"))
        print(type(event.get("size")))
        return "200 OK"
    
    elif httpMethod == "DELETE":
        try:
            table.delete_item(Key={'menu_id': event.get('param').get("menu_id")})
        except:
            return "Invalid DELETE Request 400"
        else:
            return "200 OK"
            