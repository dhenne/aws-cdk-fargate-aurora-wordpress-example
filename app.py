#!/usr/bin/env python3
from aws_cdk import core
from cdk_stacks.network import NetworkStack

from cdk_stacks.application import (
    WordpressStackProperties,
    WordpressStack
)

environment_name = "dev"
tags = [
    ['Application', 'Wordpress'],
    ['Environment', environment_name.capitalize()],
    ['Department', 'Sales']
]


app = core.App()

network_stack = NetworkStack(app, f"WordpressNetwork{environment_name.capitalize()}")

wordpress_config = WordpressStackProperties(
    vpc=network_stack.vpc,
    load_balancer=network_stack.load_balancer
)

site_none_stack = WordpressStack(
    app, f"SiteOne{environment_name.capitalize()}",
    properties=wordpress_config
)

# default tagging of all stacks
for stack in [network_stack, site_none_stack]:
    for ix in tags:
        core.Tags.of(stack).add(ix[0], ix[1])

core.Tags.of(site_none_stack).add("Customer", "SiteOne")

app.synth()
