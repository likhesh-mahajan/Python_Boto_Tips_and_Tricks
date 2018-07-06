import sys
import boto3
import logging

ec2 = boto3.resource('ec2')

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

#filters = [{'Name':'tag:Name', 'Values':['Ansible*']}]
filters = [{'Name':'instance-state-name', 'Values':['running']}]

def handler():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters=filters)

    for i in instances:
        print("Stopping : ", i)
        i.stop()

if __name__ == "__main__":
    logger = setup_logging()
    logger.info("This is a test log statement!")
    handler()

