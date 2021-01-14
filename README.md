# remediator-cdk

## Auto-remediate Security Issues in Your AWS Account

Howto Install:  
If needed, export your AWS profile:  
`export AWS_PROFILE=profile_name`

Create a virtual environment and launch the stacks:  
```
python3 -m venv .venv  
source .venv/bin/activate   
python3 -m pip install -r requirements.txt  
cdk bootstrap aws://<account-id>/<region>  
cdk synth   
cdk deploy --all
```

Set the environment remediate variable to "True" to enable auto-remediation.

Then when an administrator policy is attached, the user/role it was attached to as well as the user/role who attached it will be immediately disabled.

(c) Copyright 2020 - NickTheSecurityDude

Disclaimer:  
For informational/educational purposes only.  Bugs are likely and can be reported on github.  
Using this will incur AWS charges.
