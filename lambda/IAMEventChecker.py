import json
import boto3
import re
import os

iam_pattern=re.compile("^iam")

action_details={}

def check_action(action):
  if action == "*":
    action_details['Message']="Admin Access Detected"
    action_details['NumericSeverity']=10
    return action_details
  elif iam_pattern.match(action):
    action_details['Message']="Admin Access Detected"
    action_details['NumericSeverity']=9
    return action_details
  else:
    return None

def check_policy(statements):
  iam_flag=0
  for statement in statements:
    if statement['Effect'] == 'Allow':
      actions=statement['Action']
      if isinstance(actions, str):
        action=actions.lower()
        if check_action(action) is not None:
          iam_flag=1
      else:
        for action in statement['Action']:
          action=action.lower()
          if check_action(action) is not None:
            iam_flag=1
            
  if iam_flag==1:
    return statements
  else:
    return None

def lambda_handler(event, context):
    dangerous_events=[
      # Attach*Policy = managed policy, Put*Policy = inline policy
      "AddRoleToInstanceProfile",
      "AddUserToGroup",
      "AttachGroupPolicy",
      "AttachRolePolicy", # roleName, policyArn
      "AttachUserPolicy", # userName, policyArn
      "CreateAccessKey",
      "ConsoleLogin",
      "CreateGroup",
      "CreateInstanceProfile",
      "CreatePolicy", # policyName, policyDocument
      "CreatePolicyVersion", # policyArn, policyDocument
      "CreateRole",
      "CreateUser",
      "PutGroupPolicy",
      "PutRolePolicy", # roleName, policyName, policyDocument
      "PutUserPolicy", # userName, policyName, policyDocument
      "SetDefaultPolicyVersion",
      "UpdateAccessKey",
      "UpdateAssumeRolePolicy",
    ]

    attach_pattern=re.compile("^Attach.*Policy$")
    put_pattern=re.compile("^Put.*Policy$")

    event_name=event['detail']['eventName']
    
    iam_client = boto3.client('iam')
    
    if event_name in dangerous_events:
      print("Dangerous Event Found:", event_name)
      
      request_parameters=event['detail']['requestParameters']

      # get principle
      try:
        principle=request_parameters['userName']
      except:
        pass
      
      try:
        principle=request_parameters['roleName']
      except:
        pass
      
      try:
        principle=request_parameters['groupName']
      except:
        pass
      
      print("Principle:",principle)
      
      # if attach managed policy
      if attach_pattern.match(event_name):
        # managed
        print("Attach Event Found")
        policy_arn=request_parameters['policyArn']
        response=iam_client.get_policy(
          PolicyArn=policy_arn
        )
        
        print("Policy:",policy_arn)
        
        default_version=response['Policy']['DefaultVersionId']
        
        response=iam_client.get_policy_version(
          PolicyArn=policy_arn,
          VersionId=default_version
        )
        
        statements=response['PolicyVersion']['Document']['Statement']
        
        bad_policy=check_policy(statements)
        bad_policy_name=policy_arn
    
      # if inline policy
      elif put_pattern.match(event_name):
        #inline
        print("Put Event Found")
        #print(request_parameters)
        policy_document=json.loads(request_parameters['policyDocument'])
        #print(policy_document)
        statements=policy_document['Statement']
        #statements=json.loads(request_parameters['policyDocument']['Statement'])
        #print(statements)
        bad_policy=check_policy(statements)
        bad_policy_name="inline-policy:"+request_parameters['policyName']
        
      # end if inline
      
      else:
        bad_policy=None
        
      # end if event name block
      
      
        
      if bad_policy is not None:
        
        # build json response
        output={}
  
        output['Principle']=principle
        output['PolicyName']=bad_policy_name
        output['BadPolicy']=bad_policy
        output['Account']=event['account']
        output['Region']=event['region']
        output['Time']=event['time']
        output['RequestParameters']=request_parameters
        output['Detail']=event['detail']
        output['Alert']="Possible Dangerous IAM Policy Detected"
        #output['Severity']=10
        output['AlertDetails']=action_details
        #output['EventSource']=event['detail']['eventSource']
        #output['UserIdentity']=event['detail']['userIdentity']
        #output['EventType']=event['detail']['eventType']
        #output['EventName']=event['detail']['eventName']
        #output['SourceIPAddress']=event['detail']['sourceIPAddress']
        #output['UserAgent']=event['detail']['userAgent']
        
        print("bad policy found")
        print(bad_policy)
        print(output)
        
        # Publish to SNS
        acct_id=context.invoked_function_arn.split(":")[4]
        region=context.invoked_function_arn.split(":")[3]

        sns_arn="arn:aws:sns:"+region+":"+acct_id+":DatadogSNSTopic"
        sns_client = boto3.client('sns')
        response = sns_client.publish(
          TargetArn=sns_arn,
          Message=json.dumps(output),
        )

        if os.environ['remediate']=='True':        
          if action_details['NumericSeverity'] == 10:
            print("Auto-remediating event...")
            sns_arn="arn:aws:sns:"+region+":"+acct_id+":remediator-topic"
      
            response = sns_client.publish(
              TargetArn=sns_arn,
              Message=json.dumps(output),
            )
        else:
          print("Auto-remediation Off")
      
      else:
        print("Policy not bad")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

