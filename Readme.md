[![Build Status](https://github.com/dhenne/aws-cdk-fargate-aurora-wordpress-example/actions/workflows/test.yml/badge.svg)](https://github.com/dhenne/aws-cdk-fargate-aurora-wordpress-example/actions/workflows/test.yml)

# aws cdk fargate aurora serverless wordpress example

This repository is an example showing how to deploy
wordpress to aws fargate with ALBv2,aurora serverless and elastic file system (EFS) using the aws cdk.

## quickstart
To setup your local environment:

```
pipenv install && pipenv shell
npm install
export $PATH:$(pwd)/node_modules/.bin
```

now you are ready to deploy to your aws account

```
cdk deploy --require-approval never --all
```
