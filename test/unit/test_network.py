import json
import pytest

from aws_cdk import core
from cdk_stacks.network import NetworkStack


@pytest.fixture()
def template():
    app = core.App()
    NetworkStack(app, "NetworkStackTest")
    return json.dumps(app.synth().get_stack("NetworkStackTest").template)


def test_vpc_created(template):
    assert("AWS::EC2::VPC" in template)


def test_load_balancer_created(template):
    assert ("AWS::EC2::EIP" in template)
    assert("AWS::ElasticLoadBalancingV2::LoadBalancer" in template)
