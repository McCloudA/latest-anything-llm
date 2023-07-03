from __future__ import print_function


## HOW TO USE:
# Use the user-ID and whatever job question you want to answer, on the computer running AnythingLLM:

# python answer_open_questions.py 4650cd8e-a5ec-441c-93c8-9b716b652fe3 "How has your work history prepared you to manage a department?"

# And an answer will be sent to stdio/the command line.  Feel free to add > answerfile.txt or whatever.

import sys
import json
import os
import re
import requests
import json
import yaml
import boto3
from decimal import Decimal

def answer_question(id, question_text):

    sys.path.insert(1,'/Users/aaronmccloud/_work/weekendWork/cheeki/automatic-job-applications/latest-anything-llm/')
    sys.path.insert(1,'/Users/aaronmccloud/_work/weekendWork/cheeki/automatic-job-applications/latest-anything-llm/enrichment')

    from transcript_helpers import TranscriptEmbedder
    from jd_tools import CheekiFileHandler

    #dynamo_people_table_name = 'cheeki-job-automation-user-table'
    # our credentials file:
    credentials_filename = "../enrichment/credentials.yml"

    #s3_bucket_name = 'job-automation-uploads'
    #s3_bucket_prefix = 'public'

    with open(credentials_filename, 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
        our_chatgpt_key = cfg['creds']['chatgpt_key']
        # AWS credentials
        aws_access_key_id = cfg['creds']['aws_access_key']
        aws_secret_access_key = cfg['creds']['aws_secret_key']
        aws_region_name = 'us-west-2'  # Replace with your desired AWS region

    #domain_name = 'test_aaron_text'

    # set up the variou handlers we'll need:
    filehandler = CheekiFileHandler()

    # where the text files are
    anythingllm_summarydir = '/home/frog/repos/latest-anything-llm'
    # where AnythingLLM is installed
    anythingllm_rootdir = '/home/frog/repos/anything-llm'


    embedded_documents = TranscriptEmbedder()
    user_has_workspace = embedded_documents.does_workspace_exist(id)
    returned_answer = "User Not Embedded - Invalid Answer."
    if user_has_workspace:
        #print('Asking questions about fully-embedded applicant #',id)
        embedded_documents.set_up_by_domain_name(id,anythingllm_summarydir, anythingllm_rootdir )
        question_string = 'how would this individual answer the job application question, \'' + question_text + '\' ?  Please just write a text answer likely to result in them being hired.'
        returned_answer_json = json.loads(embedded_documents.return_simple_query(question_string))
        returned_answer = returned_answer_json['textResponse']
    return returned_answer


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Please provide exactly two command-line arguments: UID and question_text.")
    else:
        uid = sys.argv[1]
        question_text = sys.argv[2]

        # Save the current stdout and redirect it to a temporary file
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')  # Redirect to null device

        result = answer_question(uid, question_text)

        # Restore the original stdout and close the temporary file, then print our result
        sys.stdout = original_stdout
        print(result)
        sys.stdout.close()