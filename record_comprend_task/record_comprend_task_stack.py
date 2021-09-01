from aws_cdk import (
    core,
    aws_lambda,
    aws_events,
    aws_iam as iam,
    aws_dynamodb as aws_dynamodb
)

import aws_cdk.aws_s3 as _s3
from aws_cdk import aws_s3_notifications as s3_notifications

from aws_cdk.aws_lambda_event_sources import DynamoEventSource, StreamEventSource

#import aws_cdk.aws_dynamodb as aws_dynamodb

"""
from aws_dynamodb import (
    Table,
    Attribute,
    AttributeType,
    StreamViewType,
    BillingMode
)
"""

class RecordComprendTaskStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        #get context values
        instance_id = self.node.try_get_context("instanceId")
        contact_flow_id = self.node.try_get_context("contactFlowId")
        event_source_arn = self.node.try_get_context("eventSourceArn")

        # create dynamo table
        tracking_task_table = aws_dynamodb.Table(
            self, "TrackingTaskTable",
            table_name="TrackingTask",
            partition_key=aws_dynamodb.Attribute(
                name="ContactId",
                type=aws_dynamodb.AttributeType.STRING
            ),
            #stream=aws_dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        #tracking_task_table.table_stream_arn

        # create lambda to manage tracking_task_tabl
        tracking_task_lambda_role = iam.Role(scope=self, id='tracking_task_lambda_role',
                                assumed_by =iam.ServicePrincipal('lambda.amazonaws.com'),
                                role_name='tracking_task_lambda_role',
                                managed_policies=[
                                    iam.ManagedPolicy.from_aws_managed_policy_name(
                                        'service-role/AWSLambdaVPCAccessExecutionRole'),
                                    iam.ManagedPolicy.from_aws_managed_policy_name(
                                        'AmazonDynamoDBFullAccess')
                                ])
        tracking_task_lambda = aws_lambda.Function(scope=self, id="tracking_task_lambda_function",
                                                runtime=aws_lambda.Runtime.PYTHON_3_8,
                                                handler="TrackContactTask.lambda_handler",
                                                code=aws_lambda.Code.from_asset("./assets", exclude=["**", "!TrackContactTask.py"]),
                                                description='Lambda function to track contact info and task created for the contact',
                                                timeout=core.Duration.seconds(10),
                                                role=tracking_task_lambda_role,                                                
                                                )
        
        # grant permission to lambda to write to demo table
        # tracking_task_table.grant_read_write_data(tracking_task_lambda)

        
        #create proper policies for the lambda role 
        comprehend_task_lambda_role = iam.Role(scope=self, id='comprehend_task_lambda_role',
                                assumed_by =iam.ServicePrincipal('lambda.amazonaws.com'),
                                role_name='comprehend_task_lambda_role',
                                managed_policies=[
                                    iam.ManagedPolicy.from_aws_managed_policy_name(
                                        'service-role/AWSLambdaVPCAccessExecutionRole'),
                                    iam.ManagedPolicy.from_aws_managed_policy_name(
                                        'AmazonDynamoDBFullAccess'),
                                    iam.ManagedPolicy.from_aws_managed_policy_name(
                                        'ComprehendFullAccess'),
                                    iam.ManagedPolicy.from_aws_managed_policy_name(
                                        'ComprehendMedicalFullAccess'),
                                    iam.ManagedPolicy.from_aws_managed_policy_name(
                                        'AmazonConnect_FullAccess'),
                                ])
        # create lambda to comprehend and create task
        comprehend_task_lambda = aws_lambda.Function(self, "comprehend_task_lambda_function",
                                                runtime=aws_lambda.Runtime.PYTHON_3_8,
                                                handler="ComprehendTask.lambda_handler",
                                                code=aws_lambda.AssetCode("./assets", exclude=["**", "!ComprehendTask.py"]),
                                                description='Lambda function to get the transcribed text, comprehend, and create task',
                                                timeout=core.Duration.seconds(15),
                                                role=comprehend_task_lambda_role,
                                                environment={
                                                    'INSTANCE_ID': instance_id,
                                                    'CONTACT_FLOW_ID': contact_flow_id
                                                    }
                                                )
        
        # add trigger on the dynamo_db
      
        comprehend_task_lambda.add_event_source_mapping("contact_details_trigger", 
            event_source_arn=event_source_arn,
            batch_size=10,
            starting_position=aws_lambda.StartingPosition.LATEST
        )
        #comprehend_task_lambda.add_event_source(DynamoEventSource(tracking_task_table, starting_position=aws_lambda.StartingPosition.LATEST, batch_size=10))