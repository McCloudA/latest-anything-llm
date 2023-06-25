from __future__ import print_function

from transcript_helpers import TranscriptEmbedder
import json
import os
import re
import requests
import json

domain_name = 'test_aaron_text'

# where the text files are
anythingllm_summarydir = '/Users/aaronmccloud/Downloads/latestanythingllmcode'
# where AnythingLLM is installed
anythingllm_rootdir = '/Users/aaronmccloud/Downloads/anything-llm'

embedded_documents = TranscriptEmbedder()

# Subsequent times we'd like to address this person/tenant/domain again:
embedded_documents.set_up_by_domain_name(domain_name,anythingllm_summarydir, anythingllm_rootdir )

#embedded_documents.return_fuzzy_mentions('The cost of the service')
#embedded_documents.return_fuzzy_mentions('technical skills')
embedded_documents.return_simple_query('what technical skills does the applicant have?')