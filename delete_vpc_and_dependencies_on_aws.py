import boto3
from botocore.exceptions import ClientError

def delete_vpc(vpc_id):
    ec2 = boto3.resource('ec2')
    client = boto3.client('ec2')

    vpc = ec2.Vpc(vpc_id)

    # Disassociate and release Elastic IPs
    addresses = client.describe_addresses(Filters=[{'Name': 'domain', 'Values': ['vpc']}])
    for address in addresses['Addresses']:
        if 'AssociationId' in address:
            print(f"Disassociating Elastic IP {address['PublicIp']} with AssociationId {address['AssociationId']}")
            client.disassociate_address(AssociationId=address['AssociationId'])
        print(f"Releasing Elastic IP {address['PublicIp']} with AllocationId {address['AllocationId']}")
        client.release_address(AllocationId=address['AllocationId'])

    # Terminate EC2 instances
    instances = client.describe_instances(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            print(f"Terminating instance {instance_id}")
            client.terminate_instances(InstanceIds=[instance_id])
            waiter = client.get_waiter('instance_terminated')
            waiter.wait(InstanceIds=[instance_id])

    # Delete NAT gateways
    nat_gateways = client.describe_nat_gateways(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for nat_gateway in nat_gateways['NatGateways']:
        nat_gateway_id = nat_gateway['NatGatewayId']
        print(f"Deleting NAT gateway {nat_gateway_id}")
        client.delete_nat_gateway(NatGatewayId=nat_gateway_id)
        waiter = client.get_waiter('nat_gateway_deleted')
        waiter.wait(NatGatewayIds=[nat_gateway_id])

    # Detach and delete Internet Gateways
    for igw in vpc.internet_gateways.all():
        print(f"Detaching Internet Gateway {igw.id}")
        vpc.detach_internet_gateway(InternetGatewayId=igw.id)
        print(f"Deleting Internet Gateway {igw.id}")
        igw.delete()

    # Delete network interfaces
    network_interfaces = client.describe_network_interfaces(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for interface in network_interfaces['NetworkInterfaces']:
        interface_id = interface['NetworkInterfaceId']
        if interface['Status'] == 'in-use':
            attachment_id = interface['Attachment']['AttachmentId']
            print(f"Detaching network interface {interface_id} with attachment {attachment_id}")
            client.detach_network_interface(AttachmentId=attachment_id)
            waiter = client.get_waiter('network_interface_available')
            waiter.wait(NetworkInterfaceIds=[interface_id])
        print(f"Deleting network interface {interface_id}")
        client.delete_network_interface(NetworkInterfaceId=interface_id)

    # Delete route table associations and routes
    for rt in vpc.route_tables.all():
        for association in rt.associations:
            if not association.main:
                print(f"Disassociating route table {rt.id} association {association.id}")
                client.disassociate_route_table(AssociationId=association.id)
        for route in rt.routes:
            if route.origin == 'CreateRoute':
                print(f"Deleting route {route.destination_cidr_block} from route table {rt.id}")
                client.delete_route(RouteTableId=rt.id, DestinationCidrBlock=route.destination_cidr_block)
        rt.reload()
        if not rt.associations:
            print(f"Deleting route table {rt.id}")
            rt.delete()

    # Delete subnets
    for subnet in vpc.subnets.all():
        print(f"Deleting subnet {subnet.id}")
        subnet.delete()

    # Delete security groups
    for sg in vpc.security_groups.all():
        if sg.group_name != 'default':
            try:
                print(f"Deleting security group {sg.id}")
                sg.delete()
            except ClientError as e:
                if 'DependencyViolation' in str(e):
                    print(f"Skipping security group {sg.id} due to dependency violation: {e}")
                else:
                    raise

    # Delete network ACLs
    for acl in vpc.network_acls.all():
        if not acl.is_default:
            print(f"Deleting network ACL {acl.id}")
            acl.delete()

    # Detach and delete Internet Gateways (try again to ensure all dependencies are cleared)
    for igw in vpc.internet_gateways.all():
        try:
            print(f"Final attempt to detach and delete Internet Gateway {igw.id}")
            vpc.detach_internet_gateway(InternetGatewayId=igw.id)
            igw.delete()
        except ClientError as e:
            print(f"Error detaching/deleting IGW: {e}")

    # Delete the VPC
    try:
        print(f"Deleting VPC {vpc_id}")
        vpc.delete()
        print(f"VPC {vpc_id} and all its dependencies have been deleted.")
    except ClientError as e:
        print(f"Error deleting VPC {vpc_id}: {e}")


# Replace with your VPC ID
vpc_id = 'vpc-0915b9cda05e57a5c'
delete_vpc(vpc_id)
