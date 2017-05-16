from __future__ import print_function

import boto3
import json
import time
from time import strftime



print('Loading function')


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


    ordertable = dynamodb.Table('PizzaOrders')
    menutable = dynamodb.Table('PizzaMenus')
    
    httpMethod = event.get('httpMethod')
    data = event.get('data')

    if httpMethod == "POST":    
        try:
            myorder = {}
            myorder["selection"] = "empty"
            myorder["size"] = "empty"
            myorder["costs"] = "empty"
            myorder["order_time"] = strftime("%m-%d-%Y@%H:%M:%S", time.localtime())
            response = ordertable.put_item(
               Item={
                   "menu_id":data["menu_id"],
                    "order_id" : data["order_id"],
                    "customer_name" : data["customer_name"],
                    "customer_email" : data["customer_email"],
                    "order" : myorder
               }
            )
        except:
            return "invalid POST request 400"
        else:
            selection_entries = menutable.get_item(
                Key={"menu_id": data["menu_id"]}
            ).get('Item').get('selection')
            selection_list = ""
            i = 1
            for se in selection_entries:
                selection_list += str(i) +". "+ se
                if i < len(selection_entries):
                    selection_list += ", "
                i = i + 1
            post_response = "Hi " + data["customer_name"] +", please choose one of these selection: " + selection_list
            return post_response
            
    elif httpMethod == "GET":
        try:
            response = ordertable.get_item(
                Key={"order_id":event.get('param').get("order_id")}
            )
        except:
            return "Invalid GET Request 400"
        else:
            return response["Item"]
            
    elif httpMethod == "PUT":
        order_object = ordertable.get_item(
            Key={"order_id":event.get('param').get("order_id")}
        ).get('Item')
        selection_value = order_object.get('order').get('selection')
        size_value = order_object.get('order').get('size')

        if selection_value == "empty":
            
            menu_object = menutable.get_item(
                Key={"menu_id": order_object.get('menu_id')}
            ).get('Item')
            
            new_selection_value = menu_object.get('selection')[int(event.get('user_input'))-1]
            
            curr_order = ordertable.get_item(
                Key={"order_id":event.get('param').get("order_id")}
            ).get('Item').get("order")
            
            curr_order["selection"] = new_selection_value
            
            response_update_selection =  ordertable.update_item(
                Key={'order_id': event.get('param').get("order_id")},
                UpdateExpression="SET #order = :ss",
                ExpressionAttributeNames={'#order': 'order'},
                ExpressionAttributeValues={':ss': curr_order}
            )
            
            size_entries = menu_object.get('size')
            size_list = ""
            i = 1
            for se in size_entries:
                size_list += str(i) +". "+ se
                if i < len(size_entries):
                    size_list += ", "
                i = i + 1
                
            post_response = "Which size do you want? " + size_list
            
            return post_response
            
        elif size_value == "empty":
            
            menu_object = menutable.get_item(
                Key={"menu_id": order_object.get('menu_id')}
            ).get('Item')
            
            new_size_value = menu_object.get('size')[int(event.get('user_input'))-1]
            new_cost_value = menu_object.get('price')[int(event.get('user_input'))-1]

            curr_order = ordertable.get_item(
                Key={"order_id":event.get('param').get("order_id")}
            ).get('Item').get("order")
            
            curr_order["size"] = new_size_value
            curr_order["costs"] = new_cost_value
            
            response_size_selection =  ordertable.update_item(
                Key={'order_id': event.get('param').get("order_id")},
                UpdateExpression="SET #order = :ss",
                ExpressionAttributeNames={'#order': 'order'},
                ExpressionAttributeValues={':ss': curr_order}
            )
            
            post_response = "Your order costs $" +new_cost_value +". We will email you when the order is ready. Thank you!"
            
            return post_response
