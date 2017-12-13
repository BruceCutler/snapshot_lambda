import boto3
import logging
from datetime import date, timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Connect to the EC2 client and gather instance reservations
ec2 = boto3.client('ec2')

def lambda_handler(event, context):

    # Empty list to store instances
    instanceList = []
    
    reservations = ec2.describe_instances(Filters=[{'Name':'instance-state-name','Values':['running','stopped']}])['Reservations']
    
    # Loop through the reservations, gather individual instances and store in list
    for reservation in reservations:
        for instance in reservation['Instances']:
            instanceList.append(instance)
    
    try:
        # Run the createSnapshots function
        createSnapshots(instanceList)
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        
    try:
        # Run the cleanupSnapshots function
        cleanupSnapshots()
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
            
def createSnapshots(instancesList):
    print "Running createSnapshots function..."
    # Get instances, their volumes and snapshot expiration times
    for instance in instancesList:
        instanceId = instance['InstanceId']
        expiration = expirationDate(instance)
        volumes = getInstanceVolumes(instance)
        print("Instance: "+instanceId)
        print("Snapshot Expiration:"+str(expiration))
        
      # Create the snapshots and add the expiration tag
        for volume in volumes:
          desc = "Instance: " + instanceId + " / Volume: " + volume
          snap = ec2.create_snapshot(
            Description=desc,
            VolumeId=volume
          )
          snapId = snap['SnapshotId']
          addTagsToSnapshot(snapId,expiration)
          
    print('------')
    print "Snapshot creation complete!"
    print('------')

def addTagsToSnapshot(snapId,expiration):
    print "Adding Tags to snapshot..."
    tag = ec2.create_tags(
        Resources=[snapId
        ],
        Tags=[
        {
            'Key': 'Expiration',
            'Value': str(expiration)
        }
        ]
    )

def getInstanceVolumes(instance):
    volumeList=[]
    for device in instance['BlockDeviceMappings']:
        if device['Ebs'] is not None:
            volumeList.append(device['Ebs']['VolumeId'])  
    return volumeList

def expirationDate(instance):
    for tag in instance['Tags']:
        if tag['Key'] == 'Environment' and 'prod' in tag['Value'].lower():
            return date.today() + timedelta(days=30)
        else:
            continue
    return date.today() + timedelta(days=5)

def cleanupSnapshots():
    print "Running cleanupSnapshots function..."
    # Get list of snapshot ID's
    snapshots = ec2.describe_snapshots(OwnerIds=['xxxxxxxxxxx'])
    for snapshot in snapshots['Snapshots']:
        snapId = snapshot['SnapshotId']
        result = checkExpiration(snapId)
        if result:
            print("Deleting snapshot:"+snapId)
            delete = ec2.delete_snapshot(SnapshotId=snapId)
        else:
            continue

    print('------')
    print "Snapshot cleanup complete!"
    print('------')

def checkExpiration(id):
    tags = ec2.describe_tags(Filters=[{'Name':'resource-id','Values':[id]}])['Tags']
    today = str(date.today())
    for tag in tags:
        if tag['Key'] == 'Expiration' and tag['Value'] < today:
            return True
        else:
            continue
    return False