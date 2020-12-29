########################################################################################
#
# events_stack.py
#
# Resources:
#   events rule
#   events rule target
#
# Imports:  
#   lambda function: iam_event_checker
#
########################################################################################

from aws_cdk import (
  aws_events as events,
  aws_iam as iam,
  aws_events_targets as targets,
  aws_lambda as lambda_,
  core
)

class EventsStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, iam_event_checker_func: lambda_.IFunction,  **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # create events bus rule, using the default bus
    events_rule=events.Rule(self,"IAM Events Rule",
      description="IAM Events Rule",
      rule_name="remediator-iam-events",
      # use the default event bus
      #event_bus=self._cloudtrail_bus,
      event_pattern=events.EventPattern(
        source=["aws.iam"],
        detail_type=["AWS API Call via CloudTrail"],
        detail={
          "eventSource": [
            "iam.amazonaws.com"
          ]
        }
      )
    )

    # add the lambda function as a target to the events rule
    events_rule.add_target(targets.LambdaFunction(
        handler=iam_event_checker_func
      )
    )

