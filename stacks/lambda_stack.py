##############################################################
#
# lambda_stack.py
#
# Resources:
#  2 lambda functions (code in /lambda folder (from_asset))
#
# Exports:
#  2 lambda IFunctions
#
# Imports:
#  Lambda Execution Role - remediator_lambda_role
#
##############################################################

from aws_cdk import (
  aws_iam as iam,
  aws_lambda as lambda_,
  core
)

class LambdaStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, remediator_lambda_role: iam.IRole, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # create the Event Checker Lambda function
    # zip file contains a single .py file for the function
    # auto-remediate is set to False by default, change to True here or in the console to auto-remediate
    self._iam_event_checker_func=lambda_.Function(self,"IAMEventChecker Lambda Func",
      code=lambda_.Code.from_asset("lambda/IAMEventChecker.zip"),
      handler="IAMEventChecker.lambda_handler",
      runtime=lambda_.Runtime.PYTHON_3_8,
      role=remediator_lambda_role,
      environment={'remediate': 'False'}
    )

    # lambda function to do the auto-remediation
    self._iam_remediator_func=lambda_.Function(self,"IAMRemediator Lambda Func",
      code=lambda_.Code.from_asset("lambda/IAMRemediator.zip"),
      handler="IAMRemediator.lambda_handler",
      runtime=lambda_.Runtime.PYTHON_3_8,
      role=remediator_lambda_role
    )

  # Exports
  @property
  def iam_event_checker_func(self) -> lambda_.IFunction:
    return self._iam_event_checker_func

  @property
  def iam_remediator_func(self) -> lambda_.IFunction:
    return self._iam_remediator_func

