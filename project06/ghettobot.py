import os
from slackclient import SlackClient
import time
import logging
import sys
import boto3
import re
import logging
import urllib
import random
from botocore.exceptions import ClientError
from boto3.session import Session
import datetime
import requests
from tabulate import tabulate
import urllib.request
import json
import decimal


ec2client = boto3.client('ec2', region_name='us-west-2')
s = boto3.session.Session(region_name="us-east-1")



BOT_NAME = ''
SLACK_BOT_TOKEN = ''
BOT_ID = ''


# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = 'help'
COMMAND_LIST = ['help', 'show instances', 'do something', 'show me some code','show tagged', 'hackernews']
channel = ''
command = 'help'

slack_client = SlackClient(SLACK_BOT_TOKEN)

sample_code = r'''
def help_handler(command, channel):
   response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + "* command with numbers, delimited by spaces."
    if command.startswith(EXAMPLE_COMMAND):
        out_text = "Here are the commands I can run right now!" + "\n"
        for command in COMMAND_LIST:
            out_text += ">" + command + ' ' + "\n"
    slack_client.api_call("chat.postMessage", channel=channel, text=out_text, as_user=True)
'''

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

def hacker_handler(command):
    print(command)
    out_text = "Here's a list of the top 10 news articles: \n"
    url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
    r = requests.get(url)
    submission_ids = r.json()
    submission_dicts = []
    for submission_id in submission_ids[:10]:
        url = ('https://hacker-news.firebaseio.com/v0/item/' + str(submission_id) + '.json')
        submission_r = requests.get(url)
        response_dict = submission_r.json()
        time = response_dict['time']
        today = datetime.datetime.fromtimestamp(time).strftime('%c')
        if not 'url' in response_dict:
            link = "No Link, only comments"
        else:
            link = response_dict['url']
        mytitle = response_dict['title']
        myscore = response_dict['score']
        out_text += "****" + "Date : " + today + ' ' + "****" + ' ' + "Title : " + mytitle + ' ' + "****" + ' ' + "Score : " + str(myscore) + ' ' + "****" + ' ' + "Link : " + ' ' + "<" + link + ">" + "\n"
    slack_client.api_call("chat.postMessage", channel=channel, text=out_text, as_user=True)


def random_handler(command, channel):
    response = "Im in the handl_command function but not matching any code."
    if command.startswith('show me some code'):
        message = '``` ' + sample_code + ' ```'
        slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)
    elif command.startswith('do something'):
        response = "Sure...write some more code then I can do that!"
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def help_handler(command, channel):
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + "* command with numbers, delimited by spaces."
    if command.startswith(EXAMPLE_COMMAND):
        out_text = "Here are the commands I can run right now!" + "\n"
        for command in COMMAND_LIST:
            out_text += ">" + command + ' ' + "\n"
        slack_client.api_call("chat.postMessage", channel=channel, text=out_text, as_user=True)

def aws_handler(command, channel):
    if command.startswith('show tagged'):
        out_text = "Here's a list of your tagged instances: \n"
        allRegions = [region['RegionName'] for region in ec2client.describe_regions()['Regions']]
        for region in allRegions:
            if region == 'us-east-1':
                myec2 = s.resource('ec2', region_name="us-east-1")
                logger.info("message: " + "Hello from " + region)
                for i in myec2.instances.all():
                    if not i.tags:
                        out_text += "Region : " + region + ' ' +  "Instance Id : " + i.id + ' ' + "Name : " + "Not Tagged" + "\n"
                    else:
                        for tag in i.tags:
                            if tag['Key'] == 'Name':
                                instance_value_name = tag['Value']
                                out_text += ">>>> " + "Region : " + region + ' ' +  "Instance Id : " + i.id + ' ' + "Name : " + instance_value_name + "\n"
                                break
            if region == 'us-west-2':
                myec2 = s.resource('ec2', region_name="us-west-2")
                logger.info("message: " + "Hello from " + region)
                for i in myec2.instances.all():
                    if not i.tags:
                        out_text += "Region : " + region + ' ' +  "Instance Id : " + i.id + ' ' + "Name : " + "Not Tagged" + "\n"
                    for tag in (i.tags or []):
                        if tag['Key'] == 'Name':
                            instance_value_name = tag['Value']
                            out_text += "Region : " + region + ' ' +  "Instance Id : " + i.id + ' ' + "Name : " + instance_value_name + "\n"
                            break
        slack_client.api_call("chat.postMessage", channel=channel, text=out_text, as_user=True)


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(),output['channel']
    return None, None



DECISION_MAP = {
    'help': help_handler,
    'show me some code': random_handler,
    'do something': random_handler,
    'show tagged': aws_handler,
    'hackernews' : hacker_handler
}

def decision_func(input_var, command, channel):
    func = DECISION_MAP[input_var]
    func(command, channel)




if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    logger = setup_logging()
    logger.info("This is a test log statement!")

    if slack_client.rtm_connect():
        logger.info("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                logger.info('This command was called  %s', command)
                bot_command = command.strip().lower()
                if bot_command in COMMAND_LIST:
                    decision_func(bot_command, command, channel)
                else:
                    response = "Sure...write some more code then I can do that!"
                    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")


