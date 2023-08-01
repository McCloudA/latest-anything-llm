from __future__ import print_function

import sys
import json
import os
import re
import requests
import json
import yaml
import boto3
from decimal import Decimal

# TODO: instead of local file handoff, make a structure to use the API to send in files instead.  Then check the backup for this, plus backup pinecone.

class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return str(obj)
    if isinstance(obj,np.ndarray):
      return obj.tolist()
    return json.JSONEncoder.default(self, obj)
  

#sys.path.insert(1,'/Users/aaronmccloud/_work/weekendWork/cheeki/automatic-job-applications/latest-anything-llm//python_db_tests')
sys.path.insert(1,'/Users/aaronmccloud/_work/weekendWork/cheeki/automatic-job-applications/latest-anything-llm/')
from jd_tools import ContentEmbedder, JobScorer, CheekiFileHandler

from transcript_helpers import TranscriptEmbedder

# NOTE: Overrides - flip one of these and we'll remake that set of data for everyone:
address_override = False
skills_override = False
educationalBackground_override = False 
workHistory_override = False 

dynamo_people_table_name = 'cheeki-job-automation-user-table'
# our credentials file:
credentials_filename = "./credentials.yml"

s3_bucket_name = 'job-automation-uploads'
s3_bucket_prefix = 'public'

with open(credentials_filename, 'r') as ymlfile:
   cfg = yaml.safe_load(ymlfile)
   our_chatgpt_key = cfg['creds']['chatgpt_key']
   # AWS credentials
   aws_access_key_id = cfg['creds']['aws_access_key']
   aws_secret_access_key = cfg['creds']['aws_secret_key']
   aws_region_name = 'us-west-2'  # Replace with your desired AWS region

#domain_name = 'test_aaron_text'

past_data = None # do we already have a file to start from?
if os.path.isfile("active_users_details.json"): # if we do...
    # then use this as the past data/start from here...           
    with open("active_users_details.json") as pastfile:
        past_data = json.load(pastfile)
    # and also hang onto this for future use, since we'll overwrite it at the end of this script:
    with open("active_users_details_past.json", "w") as outfile:
            outfile.write(json.dumps(past_data, indent=4, cls=DecimalEncoder))

# set up the variou handlers we'll need:
filehandler = CheekiFileHandler()

# where the text files are
anythingllm_summarydir = '/home/frog/repos/latest-anything-llm'
# where AnythingLLM is installed
anythingllm_rootdir = '/home/frog/repos/anything-llm'

#embedded_documents = TranscriptEmbedder()
#embedded_documents.return_fuzzy_mentions('The cost of the service')
#embedded_documents.return_fuzzy_mentions('technical skills')
#embedded_documents.return_simple_query('what technical skills does the applicant have?')

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key,
                          region_name=aws_region_name)
# and to S3 for file IO
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, 
                  aws_secret_access_key=aws_secret_access_key, 
                  region_name=aws_region_name)
# list

# Retrieve all applicant records from the DynamoDB table
table = dynamodb.Table(dynamo_people_table_name)
table_response = table.scan()

# examples of checking for domain name existence:
#embedded_documents.does_workspace_exist('ac2345cd')
#embedded_documents.does_workspace_exist('test_aaron_text')

# NOTE:  For test, we're only going to look through the first 20 people in the DB
# TODO:  look through DB and:
# figure out which people don't have embedded records in AnythingLLM.  If they don't have one (and they do have a resume),
# then make an embedding workspace for them, named after their uid.
# for item in table_response['Items'][0:20]:
#     id = item['id']
#     print(id)
# brek
items_to_change = []
for item in table_response['Items'][0:10]: # or leave this off

    id = item['id']

    # wait - if we have a "past_data" file, and that file knows about this person, we should use that instead
    if past_data is not None:
        existing_item = [i for i in past_data if i['id']==id]
        if len(existing_item) > 0:
            item = existing_item[0]


    print('Checking out User ID: ' , id)
    print(item)
    # brek
    # Subsequent times we'd like to address this person/tenant/domain again:
    #embedded_documents.set_up_by_domain_name(uid,anythingllm_summarydir, anythingllm_rootdir )
    embedded_documents = TranscriptEmbedder()
    user_has_workspace = embedded_documents.does_workspace_exist(id)
    #check to see if we have an embedded space
    file_name = item.get('resumeFileName')
    is_complete = item.get('isInitialProfileFormCompleted')

    #if this person doesn't have a workspace yet but they do have a resume, make them a workspace and embed the resume with AnythingLLM
    if file_name and is_complete and not user_has_workspace:
        #get all the files in the folder
        #embedded_documents.delete_workspace(id)

        s3_response = s3.list_objects_v2(Bucket=s3_bucket_name, Prefix=s3_bucket_prefix + '/' + id)
        # pull the first one that matches our filename
        target_file = None
        for obj in s3_response['Contents']:
            if file_name in obj['Key']:
                target_file = obj['Key']
                break
        if target_file is not None:
            s3.download_file(s3_bucket_name, target_file, './temp_files/' + file_name)
            content = filehandler.text_from_file('./temp_files/' + file_name)
            with open(file_name + '.txt',"w") as text_file:
                text_file.write(content)

            #now set up a new worspace, in AnythingLLM, using these things:
            embedded_documents.set_up_by_filelist([file_name + '.txt'],id,anythingllm_summarydir,anythingllm_rootdir)
    
    # now, check again - if this person is already ready and encoded, check and add (if needed) the other stuff of interest, using AnythingLLM
    user_has_workspace = embedded_documents.does_workspace_exist(id)
    if is_complete and user_has_workspace:
        embedded_documents = TranscriptEmbedder()
        print('Asking questions about fully-embedded applicant #',id)
        embedded_documents.set_up_by_domain_name(id,anythingllm_summarydir, anythingllm_rootdir )
        #now check - do we have all of the pieces we'd like from this record?  If not, use AnythingLLM to get them and add them to the DB
        #look for all the pieces and fill them in as needed here!
 
        if ('address' not in item) or (item['address'] == '') or address_override:
            # make the thing of interest:
            address,city,state,zipcode = embedded_documents.get_address_set('The Applicant') # this should be the name if we have one.
            print('id: ', id)
            print('address: ', address)
            print('city: ', city)
            print('state: ', state)
            print('zipcode: ', zipcode)
            # Now let's get this specific record again, and update this record:
            if address is not None:
                item['address'] = address
                item['city'] = city
                item['state'] = state
                item['zipcode'] = zipcode
                # put (idempotent)
                #table.put_item(Item=item)

        if ('skills' not in item) or (item['skills'] == '') or skills_override:
            # make the thing of interest:
            skills = embedded_documents.get_skills_set('The Applicant')
            print('id: ', id)
            print('skills: ', skills)
            # update this record:
            if skills is not None:
                item['skills'] = skills
                #table.put_item(Item=item)
        #educationalBackground
        if ('educationalBackground' not in item) or (item['educationalBackground'] == '') or educationalBackground_override:
            # make the thing of interest:
            educationalBackground = embedded_documents.get_educationalBackground_set('The Applicant')
            print('id: ', id)
            print('educationalBackground: ', educationalBackground)
            # update this record:
            if educationalBackground is not None:
                item['educationalBackground'] = educationalBackground
                #table.put_item(Item=item)
        if ('workHistory' not in item) or (item['workHistory'] == '') or workHistory_override:
            # make the thing of interest:
            workHistory = embedded_documents.get_workHistory_set('The Applicant')
            print('id: ', id)
            print('workHistory: ', workHistory)
            # update this record:
            if workHistory is not None:
                item['workHistory'] = workHistory
                # table.put_item(Item=item)
        items_to_change.append(item)

        json_object = json.dumps(items_to_change, indent=4, cls=DecimalEncoder)
        with open("active_users_details.json", "w") as outfile:
            outfile.write(json_object)
        
        


        #embedded_documents.return_simple_query('what technical skills does the applicant have?')

# examples of checking for domain name existence:
#embedded_documents.does_workspace_exist('ac2345cd')



# export const allApplicantInfo = {
#     // This stuff we can get from our DB
#     firstName: 'Wendy',
#     lastName: 'Greene',
#     email: 'amazinganne205872@gmail.com',
#     password: 'yrdd4I!q95&k', // For patagonia, WSU, or another company
#     phone: {
#         number: '2122375678',
#         type: 'mobile'
#     },
#     // the stuff below we will need to scrape from the resume & cover letter
#     address: '5702 Green Street',
#     city: 'New York',
#     state: 'New York',
#     zipCode: '10007',
#     gender: 'female',
#     resumePath: 'resume.pdf',
#     objective: 'Motivated and enthusiastic sales/marketing assistant offering hands-on experience in the areas of sales and marketing management, sales pitching, and customer service. Possess a rich mix of knowledge in creating, implementing strategic sales and marketing programs for attainment of needed business goals. Adept at utilizing out-of-the-box techniques to identify business deficiencies and develop improved processes for optimal operational efficiency.',
#     skills: ['JavaScript', 'HTML', 'CSS', 'React', 'Node.js', 'Project Management', 'Problem Solving'],
#     websites: ['https://www.mywebsite1.com', 'https://www.mywebsite2.com'],
#     educationalBackground: [
#         {
#             institution: 'University of New York, NY',
#             degree: 'Bachelor of Science',
#             fieldOfStudy: 'Accounting',
#             startDate: ['2010', 'YYYY'],
#             endDate: ['2014', 'YYYY']
#             // All dates should be the date with -'s,
#             // and then a second string with the date format
#         }
#     ],
#     workHistory: [
#         {
#             employer: 'Dot Company',
#             position: 'Independent Sales and Marketing Coordinator',
#             location: 'New York',
#             // More examples of the date format
#             startDate: ['2021-01-01', 'YYYY-MM-DD'],
#             endDate: ['2023-02-25', 'YYYY-MM-DD'],
#             description: 'Selling via in-home and online representing and marketing line of jewelry and accessories. Engage and maintain contact with social media prospects to drive traffic to business.',
#             responsibilities: [
#                 'Realize over $1K in sales at each personal Trunk Show',
#                 'Collaborated with the team to implement new features',
#                 'Performed code reviews and provided feedback'
#             ]
#         },
#         {
#             employer: 'ABC Corporation',
#             position: 'Project Manager',
#             location: 'New York',
#             startDate: ['2018-01-01', 'YYYY-MM-DD'],
#             endDate: ['2020-12-31', 'YYYY-MM-DD'],
#             description: 'Generate new leads and prospects by successfully delivering information packets to prospective CEO’s and admissions directors of combined eight retirement communities, hospitals, and nursing homes.',
#             responsibilities: [
#                 'Led project planning and coordination efforts',
#                 'Managed project resources and budgets',
#                 'Ensured timely delivery of project milestones'
#             ]
#         }
#     ]
# };

# export default {
#     allApplicantInfo,
# };
