##########################################################################################################
#
# sns_stack.py
#
# Resources:
#   Remediate SNS Inspector
#
# Exports:
#   remediator topic arn
# 
# Imports:
#  remediator_func (lambda IFunction)
#
#########################################################################################################

from aws_cdk import (
  aws_sns as sns,
  aws_sns_subscriptions as sns_subs,
  aws_iam as iam,
  aws_lambda as lambda_,
  aws_events as events,
  core
)

class SNSStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, iam_remediator_func: lambda_.IFunction, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # create the remediator topic (lambda will push to this, which will trigger the second lambda function)
    remediator_topic=sns.Topic(self,"RemediatorTopic",
      topic_name="remediator-topic"
    )

    # subscribe the second lambda function to the topic
    remediator_topic.add_subscription(
      subscription=sns_subs.LambdaSubscription(fn=iam_remediator_func)
    )

    # create a local variable for exporting
    self._remediator_topic_arn=remediator_topic.topic_arn

  # exports
  @property
  def remediator_topic_arn(self) -> str:
    return self._remediator_topic_arn

