import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="record_comprend_task",
    version="0.0.1",

    description="A sample CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "record_comprend_task"},
    packages=setuptools.find_packages(where="record_comprend_task"),

    install_requires=[
        "aws-cdk.core==1.96.0",
        "aws-cdk.aws_iam==1.96.0",
        "aws-cdk.aws_sqs==1.96.0",
        "aws-cdk.aws_sns==1.96.0",
        "aws-cdk.aws_sns_subscriptions==1.96.0",
        "aws-cdk.aws_s3==1.96.0",
        "aws-cdk.aws_dynamodb==1.96.0",
        "aws-cdk.aws_s3_notifications==1.96.0",
        "aws-cdk.aws_lambda_event_sources==1.96.0",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: MIT No Attribution License (MIT-0)",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
