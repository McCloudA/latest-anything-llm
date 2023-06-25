import json
import os
from os.path import join
import re
import requests
import json
import shutil
import time

# TODO: Make a better summary file
# TODO: Take in a set of (phrase tag/name, phrase, exact/fuzzy) and get where/what context of each.
# TODO: create a "fill json" structure that fills a json with requested details on demand.

class TranscriptEmbedder:
    # either set this up using a list of files, or pointing at a name.
    # This class will set up (or reference) a title for the "space name," and also 
    # a set of input files that we will use for embedding.
    # this will also 

    # and also check for embedding/breakage, suggest what to do. stabilize this as much as we can!

    # The core algorithm should expect something like :
    # A title to use to describe this thing (like "Cost Concerns" or "competitor - snowflake" or whatever)
    # A list of strings corresponding to the thing (like ['this might be too expensive,' 'can we talk about overall cost, ...'])
    # A switch for determining if this is meant to be an exact match to some of this stuff or if we're trying to match the overall concept/fuzzy-match
    # An optional time frame to look for a second group in, to be delivered along with this one.
    # And then basically to return an object where we can get all the examples of the concept happening....
    def __init__(self):
        self.pinecone_domain_name = None
        self.input_file_set = None
        #self.set_params()
    
    def return_topic_conversations(self,topic):
        outstr = "We're looking for places where " + topic + " is mentioned. Reproduce every statement where " + topic + " is discussed. Structure the output as a list of json objects, one object for each mention, with the keys \'speaker_name\', and \' conversation_text\'. Do not write anything before or after this data structure."
        return outstr

    def return_topic_mentions(self,topic):
        outstr = "What is known about " + topic + "?. Reproduce every statement where the term '" + topic + "' is mentioned exactly. Structure the output as a list of json objects, one object for each mention, with the keys \'speaker_name\', and \' conversation_text\'. Do not write anything before or after this data structure."
        return outstr

    def set_params(self,anythingllm_summarydir = '/home/sean/repos/playground/sean/transcript_extraction', anythingllm_rootdir = '/home/sean/repos/anything-llm'):
        self.anythingllm_summarydir = anythingllm_summarydir # where to put the input files, and where the summary file will go.
        self.anythingllm_rootdir = anythingllm_rootdir # where is anything-llm installed
        self.anythingllm_input_dir = join(self.anythingllm_rootdir,'collector/hotdir') #where the files to be embededed go in
        self.anythingllm_check_dir = join(self.anythingllm_rootdir,'collector/hotdir/processed') # and where they come out.
        self.summary_file_name = self.pinecone_domain_name + '_sumfile.csv'
        self.summary_file_path = join(self.anythingllm_summarydir,self.summary_file_name)
    
    def set_up_by_domain_name(self, domain_name,anythingllm_summarydir, anythingllm_rootdir ): 
        self.pinecone_domain_name = domain_name
        self.set_params(anythingllm_summarydir, anythingllm_rootdir)
        return self.summary_file_path

    def set_up_by_filelist(self, list_of_input_files,domain_name,anythingllm_summarydir, anythingllm_rootdir):
        self.pinecone_domain_name = domain_name
        self.set_params(anythingllm_summarydir, anythingllm_rootdir)
        self.input_file_set = list_of_input_files

        self.migrate_input_files() # and check they made it and got encoded
        # self.create_summary_file() # and check where it went
        self.make_new_workspace() # create a new workspace for this pinecone_domain_name
        self.add_embedded_files_to_workspace()
        return self.summary_file_path
    
    def make_new_workspace(self):
        url = "http://localhost:3001/api/workspace/new"
        data = '{"name": "' + self.pinecone_domain_name + '"}'
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, data, headers=headers)

        if response.status_code == 200:
            print("POST request successful.")
        else:
            print(f"POST request failed with status code: {response.status_code}")
        content = response.text
        status_code = response.status_code
        headers = response.headers
        content_type = response.headers.get("content-type")
        print("Response Content:", content)
        print("Status Code:", status_code)
        print("Headers:", headers)
        print("Content-Type Header:", content_type)

    def add_embedded_files_to_workspace(self):
        headers = {"Content-Type": "application/json"}
        response = requests.get("http://localhost:3001/api/system/local-files", {}, headers=headers)
        keep_files = []
        for item in json.loads(response.text)['localFiles']['items'][0]['items']:
            #print('ITEM:', item)
            for fnm in self.input_file_set:
                #print('fnm: ',fnm)
                fnm_fragment = fnm.replace('/','').replace('_','-').rstrip('.').lstrip('.').lstrip('.').split('.')[0]
                if fnm_fragment.lower() in item['name'].lower():
                    keep_files.append(item['name'])
                    continue
        print('Keeping files: ')
        print(keep_files) # here are the new files relevant to this applicant

        #now go and add each file to the new workspace:
        for fname in keep_files:
            url = "http://localhost:3001/api/workspace/" + self.pinecone_domain_name + "/update-embeddings"
            data = '{"adds": ["custom-documents/' + fname + '"]}'
            print(data)
            response = requests.post(url, data, headers=headers)

            if response.status_code == 200:
                print("POST request successful.")
            else:
                print(f"POST request failed with status code: {response.status_code}")
        content = response.text
        status_code = response.status_code
        headers = response.headers
        content_type = response.headers.get("content-type")

        print("Response Content:", content)
        print("Status Code:", status_code)
        print("Headers:", headers)
        print("Content-Type Header:", content_type)
    
    def migrate_input_files(self):
        if self.input_file_set is None:
            print('This shouldn\'t happen - somehow we tried to move the input files for embedding but we don\'t have any')
            return 1
        else:
            for fte in self.input_file_set:
                source = os.path.abspath(fte)
                print('copying: ',source)
                destination = join(os.path.abspath(self.anythingllm_input_dir))
                print('to: ', destination)
                abc = shutil.copy(source, destination)
                print(abc)
                #wait a bit to let the embedding happen:
                time.sleep(2.4)
                #now let's make sure this got in and got processed:
                file_moved = os.path.isfile(join(self.anythingllm_input_dir,fte)) # actually this should have embedded
                file_embedded = os.path.isfile(join(self.anythingllm_check_dir,fte)) # and moved to here
                if file_embedded and not file_moved:
                    print('File Successfully Embedded.')
                elif file_moved and not file_embedded:
                    print('File Moved, may not have Embedded - check to be sure.')
                else:
                    print('unknown file error - go check to see what happened to these files.')
            return 0

    def create_summary_file(self):
        # read through files in self.input_file_set, in self.anythingllm_summarydir, 
        # create a summary csv file by parsing them for later,
        # and put it in self.anythingllm_summarydir
        # then return the file name
        # TODO: make this better. Later on we want to use this file for better display of results. Right now it's just a concatenation:
        if self.input_file_set is None:
            print('This shouldn\'t happen - somehow we tried to move the input files for embedding but we don\'t have any')
            return 1
        else:
            with open(self.summary_file_path, 'w') as outfile:
                for fte in self.input_file_set:
                    with open(join(self.anythingllm_check_dir,fte)) as infile:
                        outfile.write(infile.read())
            return 0


    def return_fuzzy_mentions(self,topic_text):
        url = "http://localhost:3001/api/workspace/" + self.pinecone_domain_name + "/chat"
        data = '{"message": "' + self.return_topic_mentions(topic_text) + '","mode":"query"}'
        headers = {"Content-Type": "application/json"}

        

        ret_json = None
        while ret_json is None:
            time.sleep(0.4) # avoid hitting rate limiter
            try:
                response = requests.post(url, data, headers=headers)
                if response.status_code == 200:
                    print("POST request successful.")
                else:
                    print(f"POST request failed with status code: {response.status_code}")
                content = response.text
                status_code = response.status_code
                headers = response.headers
                content_type = response.headers.get("content-type")
                print("Response Content:", content)
                print("Status Code:", status_code)
                print("Headers:", headers)
                print("Content-Type Header:", content_type)
                ret_json = json.loads(content)['textResponse'] #if this breaks, we didn't get a correct json format output
            except Exception as e:
                print('Error in Returned data structure, retrying query: ')
        return ret_json
    

    def return_simple_query(self,query_text):
        url = "http://localhost:3001/api/workspace/" + self.pinecone_domain_name + "/chat"
        print(url)
        data = '{"message": "' + query_text + '","mode":"query"}'
        print(data)
        headers = {"Content-Type": "application/json"}

        

        ret_json = None
        while ret_json is None:
            time.sleep(0.4) # avoid hitting rate limiter
            try:
                response = requests.post(url, data, headers=headers)
                if response.status_code == 200:
                    print("POST request successful.")
                else:
                    print(f"POST request failed with status code: {response.status_code}")
                content = response.text
                status_code = response.status_code
                headers = response.headers
                content_type = response.headers.get("content-type")
                print("Response Content:", content)
                print("Status Code:", status_code)
                print("Headers:", headers)
                print("Content-Type Header:", content_type)
                ret_json = content #if this breaks, we didn't get a correct json format output
            except Exception as e:
                print('Error in Returned data structure, retrying query: ')
        return ret_json


    #ret, _ = self.chatgpt_simpleresponse(prompt_text)
    #return ret
           
    # def chatgpt_simpleresponse(self, prompt_text):
    #     ret_text = None
    #     while ret_text is None:
    #         time.sleep(0.4) # avoid hitting rate limiter
    #         #remember 46,000 seconds is about 12 hours, and 
    #         # the "rate limit" stated on the OpenAI site is 200 tokens per minute
    #         #https://platform.openai.com/docs/guides/rate-limits/overview
    #         try:
    #             completion = openai.ChatCompletion.create(
    #                 model="gpt-3.5-turbo",
    #                 messages=[
    #                 {"role": "user", "content":prompt_text}
    #                 ]
    #             )
    #             ret_text = completion['choices'][0]['message']['content'].replace('\n','')
    #         except Exception as e:
    #             print('Error in API Call, retrying API embedding query: ')
    #     return ret_text , completion

