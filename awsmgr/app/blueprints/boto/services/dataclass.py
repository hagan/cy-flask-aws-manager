
from dataclasses import dataclass

#   --env AWS_ACCOUNT_ID \
#   --env AWS_ACCESS_KEY_ID \
#   --env AWS_SECRET_ACCESS_KEY \
#   --env AWS_SESSION_TOKEN \
#   --env AWS_DEFAULT_REGION \
#   --env AWS_CREDENTIAL_EXPIRATION \

@dataclass
class AWSConfig:
    aws_account_id: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_session_token: str
    aws_default_region: str = 'us-west-2'
    aws_session_token_duration: str = 900
    aws_credential_expiration: str = None
