import time
from datetime import datetime
from datetime import timedelta
import boto3
import json
from os import system, name
import os

"""
Script is for your client, make it user-friendly. So when the user executes the script, the scripts should accomplish the following:

1.  Prompt the user for an EC2 instance name
2.  Check your AWS account if the name already exists (Hint: Check the values of EC2 instances tagged with the key 'Name')
      a. If returns true, notify the user and prompt for the instance name again
      b. If returns false
          i.    Create a t3.micro EC2 instance
          ii.   Add a security group to permit SSH into the virtual machine
          iii.  Check status of the instance every 10 seconds
              1. While the EC2 instance is in the pending state, notify the user it is still pending.
              2. When the EC2 instance reaches the running state, notify the user it is running and just waiting on the health checks
3. Exit the script
"""

def ClearWindow():
    '''Function to clear the console window before the build'''

    if name == 'nt': # if windows
        _ = system('cls')

    else: # for mac and linux
        _ = system('clear')
        
def QuitFunction():
    '''Function to quit the build'''
    print()
    print()
    print('Happy Cloud Computing, Goodbye.')
    
    os._exit(-1)
    

def BuildName():
    '''Function to Build the ec2 instance using conventional naming.'''
    ClearWindow() # to clear the window

    # Still need to somehow have client log in....
    print()
    print()


    # Asks for the ec2 name, lowers and strips, quits if q or quit
    ec2UserName = input('Enter the name of the EC2 instance, q to quit: ')
    ec2UserName = ec2UserName.lower().strip()
    if ec2UserName == 'q' or ec2UserName == 'quit':
        QuitFunction()
    print()
    print()


    # Asks for the region name, lowers and strips, quits if q or quit
    regionName = input('Enter the region for the EC2, ex; us-east-2: ') 
    regionName = regionName.lower().strip()
    if regionName == 'q' or regionName == 'quit':
        QuitFunction()
    print()
    print()

    # Asks for the key-pair name, lowers and strips, quits if q or quit
    keyPairName = input('Enter the key-pair name for the EC2: ') 
    keyPairName = keyPairName.lower().strip()
    if keyPairName == 'q' or keyPairName == 'quit':
        QuitFunction()
    print()
    print()

    # Displays and confirms the conventional name.
    # Enter to confirm, q to quit, and r to rebuild name
    ec2Name = 'ec2' + '-' + regionName + '-' + ec2UserName
    print('Your ec2 instance name will be:', ec2Name)
    print('Your ec2 key-pair name will be:', keyPairName)
    conf = input('Please confirm the names: Enter to confirm, q to quit, r to retry: ')
    conf = conf.lower().strip()
    if conf == 'q':
        QuitFunction()
    elif conf == 'r':
        BuildName()
    elif conf == '':
        VerifyNameEc2(ec2Name, regionName, keyPairName)
    else:
        print('Invalid entry, Goodbye.')
        quit()

def VerifyNameEc2(ec2Name, regionName, keypairName):
    '''Function to verify the name isn't already in use'''
    print() 

    
    print()
    print('Verifying the name is not already in use....')
    resources = boto3.resource('ec2', region_name=regionName) # declaring the boto3 variable
    instances = resources.instances.all() # getting all instances with the region specified
    # testRemove = 'my-test-ec2'

    print('Current ec2 instances in region:', regionName)
    # prints the tags of all instances within the region for reference, dict form
    for instance in instances:
        try:
            print(instance.tags)
        except:
            print('Ec2 List empty')

    for instance in instances:
        # Checking all dict values in comparison to users ec2Name
        try:
            if instance.tags[0]['Value'] == ec2Name:  # use testRemove variable to test
                print('ec2 instance named already exists. Enter a new name.')
                time.sleep(5) # delayed before screen clears for name rebuild
                # if name is found then rebuild a new name
                BuildName()
            else:
                print("ec2 instance name is available.  Let's build it.")
                print()
                print()
                # if name is not found then call the build function and pass the relative information
                Buildec2(ec2Name, regionName, keypairName)  
        except:
                print("You have no ec2 instances.  Let's build one.")
                print()
                print()
                # if name is not found then call the build function and pass the relative information
                Buildec2(ec2Name, regionName, keypairName)  

def Buildec2(userEc2Name, regionName, keyPairName):
    '''This function will create the key-pair, security group, instance, start the instance, connect the security group, and check the status of the instance.  AMI id, VPC, and Subnet were already built manually earlier'''

    print('We can now build the ec2 Instance')
    print()
    print()
    
    amiId = 'ami-0fa49cc9dc8d62c84' # Amazon Linux 2
    subnetId = 'subnet-03c1fc57019bd4986' # my subnet within my vpc
    vpcId = 'vpc-01da7f68a63a18b70' # my vpc from my account
    instanceSize = 't2.micro' # Changed to t2 for free tier
    securityGroupName = 'allow-inbound-ssh'

#     USER_DATA = '''#!/bin/bash yum update''' # TODO Do I need to address this...................

    ec2Resource = boto3.resource('ec2', region_name=regionName) # declaring boto3 resource variable

    # creating the key pair, name is already defined in variables 
    keyPair = ec2Resource.create_key_pair(
        KeyName = keyPairName,
        TagSpecifications=[
            {
                'ResourceType': 'key-pair',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': keyPairName
                    },
                ]
            },
        ]
    )
    
    print(f'SSH key name:\n{keyPairName}')
    print()
    print()
    print(f'SSH key fingerprint:\n{keyPair.key_fingerprint}')
    print()
    print()
    print(f'Private SSH key:\n{keyPair.key_material}')
    print()
    print()
    print('Please copy this information for your records and for ssh login')
    print()
    print()
    print('Pausing......') 
    time.sleep(10) # Pausing to allow user copy function

    # creating security group, name is already defined in variables
    securityGroup = ec2Resource.create_security_group(
        Description = 'Allow inbound SSH traffic',
        GroupName = securityGroupName,
        VpcId = vpcId, 
        TagSpecifications=[
            {
                'ResourceType': 'security-group',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': securityGroupName
                    },
                ]
            },
        ],
    )

    # allowing all inbound and outbound ssh via port 22
    securityGroup.authorize_ingress(
        CidrIp='0.0.0.0/0',
        FromPort=22,
        ToPort=22,
        IpProtocol='tcp',
    )

    securityGroupId = securityGroup.id
    print()
    print()
    print(f'Security Group "{securityGroupName}" has been created')

    # creating the instance
    instance = ec2Resource.create_instances(
        MinCount = 1,
        MaxCount = 1,
        ImageId = amiId,
        InstanceType = instanceSize, 
        KeyName = keyPairName,
        # attaching the security group just created
        
        # SecurityGroupIds = [
        #     securityGroupId,
        # ],
        # SubnetId=subnetId,
        NetworkInterfaces=[
            {
                "DeviceIndex": 0,
                "SubnetId": subnetId,
                "Groups": [securityGroupId],
                "AssociatePublicIpAddress": True
            }
        ],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': userEc2Name
                    },
                ]
            },
        ]
    )
    # getting the instance id for future reference
    for instance in instance:
        instanceId = instance.id
      
    print()
    print()
    
    print(f'EC2 instance "{userEc2Name}" has been created and launched')
    print()
    print()
    
    # print('Start Pending......') # TODO Switch to check every ten seconds

    now = datetime.now()
    tenSeconds = datetime.now() + timedelta(seconds=10)
    instance = ec2Resource.Instance(instanceId)
    monitoringState = instance.state['Name']
    sec = 10

    print('Start Pending.', end = '')
    while True:
        time.sleep(0.25)
        print('.', end = '')
        try:
            if now > tenSeconds:
                print(sec, 'Seconds passed', end ='')
                instance = ec2Resource.Instance(instanceId)
                monitoringState = instance.state['Name']
                tenSeconds = datetime.now() + timedelta(seconds=10)
                sec += 10
                continue
            if monitoringState == 'pending':
                now = datetime.now()
                continue
            if monitoringState == 'running':
                break
        except:
            print('Unexpected error: please contact Joshua George @ Infosys support.')
            QuitFunction()
    
    print()
    print()
    print()
    print(f'EC2 instance "{userEc2Name}" has been started and is running') # TODO Still need to figure out health checks
    print()
    print()
    print(f'Security Group "{securityGroupName}" has been attached to EC2 instance {userEc2Name}')
    print()
    print()

    # printing out information
    print(f'Instance name       - {userEc2Name}')
    print(f'Instance Id         - {instanceId}')
    print(f'Security Group Name - {securityGroupName}')
    print(f'Security Group Id   - {securityGroupId}')
    print(f'Key Pair name       - {keyPairName}')
    print()
    print()
    print('The build is complete and running.  Health checks should be completed momentarily.')
    print()
    print()
    print("Thank you for choosing Infosys for your cloud computing needs\nand if you have any questions please don't\nhesitate to contact me further.\n@ jgeorge@GenericEmail.com")
    
    

    # exiting the script
    QuitFunction()

BuildName()

#     instances = ec2Resource.instances.filter(
#     InstanceIds=[
#         instanceId,
#         ],
#     )

#     for instance in instances:
#         monitoring_state = instance.monitoring['State']

#         while monitoring_state != 'enabled':
#             instance.monitor()
#             print('Instance state pending...')
#             time.sleep(10)
#         if monitoring_state == 'enabled':
#             instance.unmonitor()
#             print(f'Instance monitoring: {monitoring_state}')
#             print('Instance state is enabled, waiting on health checks')

#     response = ec2Client.describe_instance_status( # TODO this section needs addressesed
    
#     InstanceIds=[
#         instanceId,
#     ],
#     MaxResults=123,
#     NextToken='string',
#     DryRun=True|False,
#     IncludeAllInstances=True|False
#     )

#     print()


