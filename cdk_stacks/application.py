import os
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_rds as rds,
    aws_efs as efs,
    aws_ecr_assets as ecr_assets,
    aws_elasticloadbalancingv2 as elbv2,
    core
)


class WordpressStackProperties:

    def __init__(
            self,
            vpc: ec2.Vpc,
            load_balancer: elbv2.ApplicationLoadBalancer,
    ) -> None:

        self.vpc = vpc
        self.load_balancer = load_balancer


class WordpressStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str,
                 properties: WordpressStackProperties, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        database = rds.ServerlessCluster(
            self, "WordpressServerless",
            engine=rds.DatabaseClusterEngine.AURORA_MYSQL,
            default_database_name="WordpressDatabase",
            vpc=properties.vpc,
            scaling=rds.ServerlessScalingOptions(
                auto_pause=core.Duration.seconds(300)
            ),
            deletion_protection=False,
            backup_retention=core.Duration.days(7),
            removal_policy=core.RemovalPolicy.DESTROY,
        )

        file_system = efs.FileSystem(
            self, "WebRoot",
            vpc=properties.vpc,
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,
            throughput_mode=efs.ThroughputMode.BURSTING,
        )

        # docker context directory
        docker_context_path = os.path.dirname(__file__) + "../../src"

        # upload images to ecr
        nginx_image = ecr_assets.DockerImageAsset(
            self, "Nginx",
            directory=docker_context_path,
            file="Docker.nginx",
        )

        wordpress_image = ecr_assets.DockerImageAsset(
            self, "Php",
            directory=docker_context_path,
            file="Docker.wordpress",
        )

        cluster = ecs.Cluster(
            self, 'ComputeResourceProvider',
            vpc=properties.vpc
        )

        wordpress_volume = ecs.Volume(
            name="WebRoot",
            efs_volume_configuration=ecs.EfsVolumeConfiguration(
                file_system_id=file_system.file_system_id
            )
        )

        event_task = ecs.FargateTaskDefinition(
            self, "WordpressTask",
            volumes=[wordpress_volume]
        )

        #
        # webserver
        #
        nginx_container = event_task.add_container(
            "Nginx",
            image=ecs.ContainerImage.from_docker_image_asset(nginx_image)
        )

        nginx_container.add_port_mappings(
            ecs.PortMapping(container_port=80)
        )

        nginx_container_volume_mount_point = ecs.MountPoint(
            read_only=True,
            container_path="/var/www/html",
            source_volume=wordpress_volume.name
        )
        nginx_container.add_mount_points(nginx_container_volume_mount_point)

        #
        # application server
        #
        web_container = event_task.add_container(
            "Php",
            environment={
                # 'WORDPRESS_DB_HOST': database.db_instance_endpoint_address,
                'WORDPRESS_DB_HOST': database.cluster_endpoint.hostname,
                'WORDPRESS_TABLE_PREFIX': 'wp_'
            },
            secrets={
                'WORDPRESS_DB_USER': ecs.Secret.from_secrets_manager(database.secret, field="username"),
                'WORDPRESS_DB_PASSWORD': ecs.Secret.from_secrets_manager(database.secret, field="password"),
                'WORDPRESS_DB_NAME': ecs.Secret.from_secrets_manager(database.secret, field="dbname"),
            },
            image=ecs.ContainerImage.from_docker_image_asset(wordpress_image)
        )
        web_container.add_port_mappings(
            ecs.PortMapping(container_port=9000)
        )

        container_volume_mount_point = ecs.MountPoint(
            read_only=False,
            container_path="/var/www/html",
            source_volume=wordpress_volume.name
        )
        web_container.add_mount_points(container_volume_mount_point)

        #
        # create service
        #
        wordpress_service = ecs.FargateService(
            self, "InternalService",
            task_definition=event_task,
            platform_version=ecs.FargatePlatformVersion.VERSION1_4,
            cluster=cluster,
        )

        #
        # scaling
        #
        scaling = wordpress_service.auto_scale_task_count(
            min_capacity=2,
            max_capacity=50
        )
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=85,
            scale_in_cooldown=core.Duration.seconds(120),
            scale_out_cooldown=core.Duration.seconds(30),
        )

        #
        # network acl
        #
        database.connections.allow_default_port_from(wordpress_service, "wordpress access to db")
        file_system.connections.allow_default_port_from(wordpress_service)

        #
        # external access
        #
        wordpress_service.connections.allow_from(
            other=properties.load_balancer,
            port_range=ec2.Port.tcp(80)
        )

        http_listener = properties.load_balancer.add_listener(
            "HttpListener",
            port=80,
        )

        http_listener.add_targets(
            "HttpServiceTarget",
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[wordpress_service],
            health_check=elbv2.HealthCheck(healthy_http_codes="200,301,302")
        )
