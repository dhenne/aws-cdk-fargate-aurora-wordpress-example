import os
from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    core
)


class NetworkStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # vpc
        self.vpc = ec2.Vpc(
            self, "Vpc",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name="Public",
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE,
                    name="Private",
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.ISOLATED,
                    name="DB",
                    cidr_mask=24
                )
            ],
            nat_gateway_provider=ec2.NatProvider.gateway(),
            nat_gateways=2,
        )
        core.CfnOutput(self, "VpcID",
                       value=self.vpc.vpc_id)

        self.load_balancer = elbv2.ApplicationLoadBalancer(
            self, "ExternalEndpoint",
            vpc=self.vpc,
            internet_facing=True,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )

        core.CfnOutput(
            self, "ExternalDNSName",
            value=self.load_balancer.load_balancer_dns_name
        )
