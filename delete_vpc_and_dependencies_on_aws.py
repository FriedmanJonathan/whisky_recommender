import boto3


def delete_vpc(vpc_id):
    ec2 = boto3.resource('ec2')
    client = boto3.client('ec2')

    vpc = ec2.Vpc(vpc_id)

    # Disassociate and release Elastic IPs
    addresses = client.describe_addresses(Filters=[{'Name': 'domain', 'Values': ['vpc']}])
    for address in addresses['Addresses']:
        if 'AssociationId' in address:
            client.disassociate_address(AssociationId=address['AssociationId'])
        client.release_address(AllocationId=address['AllocationId'])

    # Delete NAT gateways
    nat_gateways = client.describe_nat_gateways(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for nat_gateway in nat_gateways['NatGateways']:
        client.delete_nat_gateway(NatGatewayId=nat_gateway['NatGatewayId'])
        waiter = client.get_waiter('nat_gateway_deleted')
        waiter.wait(NatGatewayIds=[nat_gateway['NatGatewayId']])

    # Detach and delete Internet Gateways
    for igw in vpc.internet_gateways.all():
        vpc.detach_internet_gateway(InternetGatewayId=igw.id)
        igw.delete()

    # Terminate EC2 instances
    instances = client.describe_instances(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            client.terminate_instances(InstanceIds=[instance_id])
            waiter = client.get_waiter('instance_terminated')
            waiter.wait(InstanceIds=[instance_id])

    # Delete network interfaces
    network_interfaces = client.describe_network_interfaces(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for interface in network_interfaces['NetworkInterfaces']:
        if interface['Status'] == 'in-use':
            client.detach_network_interface(AttachmentId=interface['Attachment']['AttachmentId'])
            waiter = client.get_waiter('network_interface_available')
            waiter.wait(NetworkInterfaceIds=[interface['NetworkInterfaceId']])
        client.delete_network_interface(NetworkInterfaceId=interface['NetworkInterfaceId'])

    # Delete route table associations and routes
    for rt in vpc.route_tables.all():
        for association in rt.associations:
            if not association.main:
                client.disassociate_route_table(AssociationId=association.id)
        for route in rt.routes:
            if route.origin == 'CreateRoute':
                client.delete_route(RouteTableId=rt.id, DestinationCidrBlock=route.destination_cidr_block)
        # Re-fetch the route table to ensure all associations and routes are gone
        rt.reload()
        if not rt.associations:
            rt.delete()

    # Delete subnets
    for subnet in vpc.subnets.all():
        subnet.delete()

    # Delete security groups
    for sg in vpc.security_groups.all():
        if sg.group_name != 'default':
            sg.delete()

    # Delete network ACLs
    for acl in vpc.network_acls.all():
        if not acl.is_default:
            acl.delete()

    # Delete the VPC
    vpc.delete()
    print(f"VPC {vpc_id} and all its dependencies have been deleted.")


# Replace with your VPC ID
vpc_id = 'vpc-097fa4cb47068753e'
delete_vpc(vpc_id)
