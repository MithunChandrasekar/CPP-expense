import boto3
from django.conf import settings

def send_sns_notification(subject, message):
    """
    Send an SNS notification to the configured topic.
    """
    sns_client = boto3.client('sns', region_name=settings.AWS_REGION_NAME)

    response = sns_client.publish(
        TopicArn=settings.AWS_SNS_TOPIC_ARN,
        Message=message,
        Subject=subject,
    )
    return response
