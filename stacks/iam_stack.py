##############################################################
#
# iam_stack.py
#
# Resources:
#   Lambda Execution Role
#    - 
#   Deny All Policy
#
# Exports:
#  lambda_execution_role_arn
#
##############################################################

from aws_cdk import (
  aws_iam as iam,
  core
)

class IAMStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, env, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # get acct id for policies
    acct_id=env['account']

    # create lambda execution role, use same role for both lambdas
    self._remediator_lambda_role=iam.Role(self,"Remediator Lambda Role",
      role_name="Remediator_Lambda_Execution_Role",
      assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
      # update the resources later
      inline_policies=[
        iam.PolicyDocument(
          statements=[iam.PolicyStatement(
            actions=["sns:Publish"],
            effect=iam.Effect.ALLOW,
            resources=["arn:aws:sns:us-east-1:"+acct_id+":remediator-topic","arn:aws:sns:us-east-1:"+acct_id+":DatadogSNSTopic"]
          )],
        ),
        iam.PolicyDocument(
          statements=[iam.PolicyStatement(
            actions=["iam:AttachGroupPolicy","iam:AttachUserPolicy","iam:AttachRolePolicy"],
            effect=iam.Effect.ALLOW,
            resources=["*"],
            conditions={
              "ArnEqualsIfExists": {
                "iam:PolicyARN": "arn:aws:iam::"+acct_id+":policy/bleu_team_deny_all"
              }
            }
          )]
      )],
      managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name('IAMReadOnlyAccess'),
        iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')  
      ]
    )

    # create deny all policy
    iam.ManagedPolicy(self,"Deny All Policy",
      managed_policy_name="bleu_team_deny_all",
      document=iam.PolicyDocument(
        statements=[iam.PolicyStatement(
          actions=["*"],
          effect=iam.Effect.DENY,
          resources=["*"]
        )]       
      )
    )

  # Exports
  @property
  def remediator_lambda_role(self) -> iam.IRole:
    return self._remediator_lambda_role


