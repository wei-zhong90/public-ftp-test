from time import sleep
import boto3
import uuid
import argparse
import time

# Parse the ips and subnets from the option
def convert_list(string):
    return string.split(",")
    

parser = argparse.ArgumentParser()
parser.add_argument('-ips', required=True, type=convert_list, help='Input a set of ips separated by comma')
parser.add_argument('-subnets', required=True, type=convert_list, help='Input a set of subnets separated by comma')
parser.add_argument('-vpcid', required=True, type=str, help='Input vpc id')
parser.add_argument('-name', required=True, type=str, help='Input a tag name for the resource')

args = parser.parse_args()

subnets = args.subnets
ip_list = args.ips
vpc_id = args.vpcid
name = args.name

# Build the client
lb = boto3.client('elbv2')

def generate_target_group(client, port, vpcid):
    response = client.create_target_group(
        Name=f'{name}-ftp-{str(uuid.uuid4())[:8]}',
        Protocol='TCP',
        Port=port,
        VpcId=vpcid,
        HealthCheckProtocol='TCP',
        HealthCheckEnabled=True,
        TargetType='ip',
        Tags=[
            {
                'Key': 'env',
                'Value': 'public_ftp'
            },
        ],
        IpAddressType='ipv4'
    )
    return response['TargetGroups'][0]['TargetGroupArn']

def modify_target_group(client, tg_arn):
    client.modify_target_group_attributes(
        TargetGroupArn=tg_arn,
        Attributes=[
            {
                'Key': 'preserve_client_ip.enabled',
                'Value': 'true'
            },
        ]
    )

def generate_load_balancer(client, subnets):
    response = client.create_load_balancer(
        Name=f'{name}-ftp-{str(uuid.uuid4())[:8]}',
        Subnets=subnets,
        Scheme='internet-facing',
        Tags=[
            {
                'Key': 'env',
                'Value': 'public_ftp'
            },
        ],
        Type='network',
        IpAddressType='ipv4'
    )
    return response['LoadBalancers'][0]['LoadBalancerArn']

def register_targets(client, ip, target_group_arn):
    client.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[
            {
                'Id': ip,
            },
        ]
    )
    
def create_listener(client, loadbalancer_arn, port, target_group_arn):
    client.create_listener(
        LoadBalancerArn=loadbalancer_arn,
        Protocol='TCP',
        Port=port,
        DefaultActions=[
            {
                'Type': 'forward',
                'TargetGroupArn': target_group_arn
            }
        ],
        Tags=[
            {
                'Key': 'env',
                'Value': 'public_ftp'
            },
        ]
    )
    
def get_loadbalancer_status(client, loadbalancer_arn):
    response = client.describe_load_balancers(
        LoadBalancerArns=[
            loadbalancer_arn,
        ]
    )
    return [response['LoadBalancers'][0]['State']['Code'], response['LoadBalancers'][0]['DNSName']]

if __name__ == "__main__":
    lb_arn = generate_load_balancer(lb, subnets)
    print("Load balancer created")
    port_list = [21] + list(range(8192,8201))
    for port in port_list:
        tg_arn = generate_target_group(lb, port, vpc_id)
        modify_target_group(lb, tg_arn)
        for ip in ip_list:
            register_targets(lb, ip, tg_arn)
        create_listener(lb, lb_arn, port, tg_arn)
        print(f"{port} is forwarded to FTP")
    state = "provisioning"
    while (state != "active"):
        state = get_loadbalancer_status(lb, lb_arn)[0]
        time.sleep(3)
    print(f"Now the load balancer is {state}")
    print(f"FTP is available at {get_loadbalancer_status(lb, lb_arn)[1]}")
      
    