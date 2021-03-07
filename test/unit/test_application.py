import json
import pytest

from aws_cdk import core
from cdk_stacks.network import NetworkStack
from cdk_stacks.application import WordpressStack
from cdk_stacks.application import WordpressStackProperties


@pytest.fixture()
def template():
    app = core.App()
    net = NetworkStack(app, "NetworkStackTest")

    properties = WordpressStackProperties(
        vpc=net.vpc,
        load_balancer=net.load_balancer
    )
    WordpressStack(app, "WordpressStackTest", properties=properties)

    return json.dumps(app.synth().get_stack("WordpressStackTest").template)


def test_persistence(template):
    assert("AWS::EFS::FileSystem" in template)
    assert("AWS::RDS::DBCluster" in template)


def test_ecs(template):
    assert ("AWS::ECS::TaskDefinition" in template)
    assert ("AWS::ApplicationAutoScaling::ScalableTarget" in template)


