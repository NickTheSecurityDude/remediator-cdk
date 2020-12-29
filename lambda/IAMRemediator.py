import json
import boto3

def deny_user(_user_name,policy):
  iam_client = boto3.client('iam')
  response = iam_client.attach_user_policy(
    UserName=_user_name,
    PolicyArn=policy
  )
  print(response)
  print("Denying all actions for user:",_user_name)
  return 1
  
def deny_role(_role_name,policy):
  iam_client = boto3.client('iam')
  response = iam_client.attach_role_policy(
    RoleName=_role_name,
    PolicyArn=policy
  )
  print(response)
  print("Denying all actions for role:",_role_name)
  return 1
  
def deny_group(_group_name,policy):
  iam_client = boto3.client('iam')
  response = iam_client.attach_group_policy(
    GroupName=_group_name,
    PolicyArn=policy
  )
  print(response)
  print("Denying all actions for group:",_group_name)
  return 1
  

def lambda_handler(event, context):
	
    print(event)
    json_msg=json.loads(event['Records'][0]['Sns']['Message'])

    acct_id=context.invoked_function_arn.split(":")[4]
    region=context.invoked_function_arn.split(":")[3]
    deny_policy="arn:aws:iam::"+acct_id+":policy/bleu_team_deny_all"
    
    #print(json_msg)
    user_type=json_msg['Detail']['userIdentity']['type']
    
    # block user/role who attached bad policy
    if user_type != 'Root':
      principal_name_caller=json_msg['Detail']['userIdentity']['arn'].split("/")[1]
      if user_type=='IAMUser':
        deny_user(principal_name_caller,deny_policy)
      else:
      	deny_role(principal_name_caller,deny_policy)
    
    # block user/role with attached bad policy
    event_name=json_msg['Detail']['eventName']
    
    if event_name == 'AttachUserPolicy':
      user_name=json_msg['Detail']['requestParameters']['userName']
      deny_user(user_name,deny_policy)
      
    if event_name == 'AttachRolePolicy':
      role_name=json_msg['Detail']['requestParameters']['roleName']
      deny_role(role_name,deny_policy)
      
    if event_name == 'AttachGroupPolicy':
      role_name=json_msg['Detail']['requestParameters']['groupName']
      deny_group(group_name,deny_policy)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

