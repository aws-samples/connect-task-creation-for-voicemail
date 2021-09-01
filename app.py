#!/usr/bin/env python3

from aws_cdk import core
import os

from record_comprend_task.record_comprend_task_stack import RecordComprendTaskStack


app = core.App()
RecordComprendTaskStack(app, "record-comprend-task", env=core.Environment(
                                                        account=os.environ["CDK_DEFAULT_ACCOUNT"],
                                                        region=os.environ["CDK_DEFAULT_REGION"]))

app.synth()
