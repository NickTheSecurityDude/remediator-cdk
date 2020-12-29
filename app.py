#!/usr/bin/env python3

###################################################################
#
# 1. IAM Stack
#   - Deny Policy
#   - Lambda Execution Role
#
# 2. Lambda Stack
#   - IAMEventChecker.py
#   - IAMRemediator.py
#
# 3. SNS Stack
#   - Remediate SNS Topic
#
# 4. Events Bridge Stack
#   - CloudTrail Bus
#   - IAM Rule
# 
###################################################################

from aws_cdk import core

import boto3
import sys

client = boto3.client('sts')
# region is always us-east-1 for this
region=client.meta.region_name

if region != 'us-east-1':
  print("This app may only be run from us-east-1")
  sys.exit()

account_id = client.get_caller_identity()["Account"]

my_env = {'region': 'us-east-1', 'account': account_id}

from stacks.iam_stack import IAMStack
from stacks.lambda_stack import LambdaStack
from stacks.sns_stack import SNSStack
from stacks.events_stack import EventsStack

proj_name="rem-demo-"

app = core.App()

iam_stack=IAMStack(app, proj_name+"iam",env=my_env)
lambda_stack=LambdaStack(app, proj_name+"lambda",
    remediator_lambda_role=iam_stack.remediator_lambda_role   
  )
sns_stack=SNSStack(app, proj_name+"sns",
    iam_remediator_func=lambda_stack.iam_remediator_func
  )
events_stack=EventsStack(app, proj_name+"events",
    iam_event_checker_func=lambda_stack.iam_event_checker_func
  )

app.synth()
