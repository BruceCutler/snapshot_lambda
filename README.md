# snapshot_lambda

## Description

A lambda function that creates and deletes EBS volume snapshots when triggered

## Method Explanation

- **createSnapshots:** Reads the 'Environment' tag associated with an EC2 instance and determines an appropriate expiration date for volume snapshots. From there, it gathers all the volumes and creates snapshots of them and ensures that they are tagged appropriately

- **cleanupSnapshots:** Retrieves all the snapshots owned by a particular account and examines their 'Expiration' tag. If todays date is past the expiration tag value, the snapshot is deleted from the account

- **expirationDate:** If the word 'prod' appears in the 'Environment' tag associated with an EC2 instance, this is set to 30 days from today. All other instances are set to 5 days from today

- **getInstanceVolumes:** Reads the EBS volume information from a particular instance if it exists

- **addTagsToSnapshot:** Adds an 'Expiration' tag to every new snapshot with the value set to the result of the expirationDate function

- **checkExpiration:** Reads the 'Expiration' tag associated with an EBS volume and returns a boolean based on whether the snapshot should be retired or not.
