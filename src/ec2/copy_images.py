import logging
import pprint
import boto3
import json
from src.utils import awsutils
from botocore.exceptions import ClientError

#logger = logging.getLogger(__name__)
#ec2 = boto3.resource('ec2')

def copy_amis(client, lst, name_prefix, KmsKeyId, waitForCompletion=True, DryRun=True):

    res_lst = []
    amis = []

    for elt in lst:
        instance_id = elt[0]
        tags = elt[1]
        description = tags["Name"]
        encrypted = True
        kms_key_id = KmsKeyId
        name = name_prefix + " " + instance_id + " " + tags["Name"]
        source_image_id = elt[2]
        source_region = 'us-east-1'

        res = client.copy_image(Description = description,
                                Encrypted = encrypted,
                                KmsKeyId = kms_key_id,
                                DryRun = DryRun,
                                Name = name,
                                SourceImageId = source_image_id,
                                SourceRegion = source_region)
        ami_id = res["ImageId"]
        pprint.pprint(ami_id)

        res_lst.append((elt[0], elt[1], elt[2], ami_id))
        amis.append(ami_id)

    if waitForCompletion:
        awsutils.wait_for_ami_completion(client, amis)

    return res_lst


# main
def main(waitForCompletion = True):
    pprint.pprint("Entering copy_images.main()")
    vars = awsutils.read_vars()
    client = awsutils.get_ec2_client('us-east-1')

    with open('input/base_amis.txt') as infile:
        lst = json.load(infile)

    #pprint.pprint(vars['KmsKeyId'])

    copied_amis = copy_amis(client, lst,
                            vars["EcsSharedPrefix"],
                            waitForCompletion = waitForCompletion,
                            KmsKeyId=vars['SourceKmsKeyId'],
                            DryRun=False)

    with open('input/copied_amis.txt', 'w') as outfile:
        json.dump(copied_amis, outfile, indent=4)

    pprint.pprint("Leaving copy_images.main()")


#main()