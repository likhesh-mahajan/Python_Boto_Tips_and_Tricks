import decimal
import os
import re
import logging
import urllib
import random
import boto3
from botocore.exceptions import ClientError
from boto3.session import Session
import sys
import datetime
import requests
from tabulate import tabulate
import urllib.request
import json
import decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def setup_logging():
    logger = logging.getLogger()
    for h in logger.handlers:
      logger.removeHandler(h)
    h = logging.StreamHandler(sys.stdout)
    FORMAT = "[%(levelname)s %(asctime)s %(filename)s:%(lineno)s - %(funcName)21s() ] %(message)s"
    h.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

    return logger





class HackerNews(object):
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

    def QueryCreate(self, tablename):
        client = boto3.client('dynamodb')

        response = client.list_tables()

        if tablename in response['TableNames']:
            table_found = True
        else:
            table_found = False
            dynamodb = boto3.resource('dynamodb')

            table = dynamodb.create_table(
                TableName = tablename,
                KeySchema=[
                    {
                        'AttributeName': 'timestamp',
                        'KeyType': 'HASH'  #Partition key
                    },
                    {
                        'AttributeName': 'title',
                        'KeyType': 'RANGE'  #Sort key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'timestamp',
                        'AttributeType': 'N'
                    },
                    {
                        'AttributeName': 'title',
                        'AttributeType': 'S'
                    },

                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
                }
            )

            table.meta.client.get_waiter('table_exists').wait(TableName=tablename)
        return table_found

    def BatchWrite(self, tablename, items):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(tablename)
        #year = 2018
        timestamp = items['time']
        title = items['title']
        info = items['url']
        score = items['score']
        user = items['by']
        table.put_item(Item={'timestamp': timestamp,'title': title, 'info': info, 'score': score, 'user': user})
        return True

    def GetHackerNews(self):
        url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
        r = requests.get(url)
        submission_ids = r.json()
        submission_dicts = []
        response_dict = {}
        for submission_id in submission_ids[:10]:
            url = ('https://hacker-news.firebaseio.com/v0/item/' + str(submission_id) + '.json')
            submission_r = requests.get(url)
            response_dict = submission_r.json()
            if not 'url' in response_dict:
                response_dict['url'] = "No Link, only comments"
            updatetable = self.BatchWrite(tablename="HackerNews", items=response_dict)

    def GetTableItems(self, tablename):
        hackernews_list_of_dicts = []
        response = {}
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(tablename)
        response = table.scan()
        for i in response['Items']:
            mytable = json.dumps(i, cls=DecimalEncoder)
            hackernews_list_of_dicts.append(mytable)

        return hackernews_list_of_dicts






if __name__ == "__main__":
    logger = setup_logging()
    logger.info("This is a test log statement!")

    hn = HackerNews()
    createsuccess = hn.QueryCreate(tablename="HackerNews")
    if createsuccess:
        print("Table has been created or already exists")
    #out_text = "Here's a list of the top 10 news articles: \n"
    hn.GetHackerNews()
    list_of_dicts = hn.GetTableItems(tablename='HackerNews')
    for i in list_of_dicts:
        print(i)

    #out_text += "****" + "Date : " + today + ' ' + "****" + ' ' + "Title : " + mytitle + ' ' + "****" + ' ' + "Score : " + str(myscore) + ' ' + "****" + ' ' + "Link : " + ' ' + "<" + link + ">" + "\n"


