[![Build Status](https://github.com/codecentric/spring-boot-admin/workflows/build/badge.svg)](https://github.com/codecentric/spring-boot-admin/actions)

# aws cdk fargate aurora wordpress example

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
