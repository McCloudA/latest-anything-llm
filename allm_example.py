from __future__ import print_function
# %% [markdown]
# # Example - Extract interesting parts from transcripts, emails etc.
# 
# Here's what we're doing here:
#  - Setting up an instance of AnythingLLM, on docker (https://github.com/Mintplex-Labs/anything-llm)
#  - Filling the LLM "hopper" with all the data from an account (transcripts, emails, etc)
#  - Adding these to the AnythingLLM "hot" directory to be embedded
#  - Asking AnythingLLM to embed that file and keep it in the database for later
#  - Asking AnythingLLM/OpenAI for details that should be in these documents, in particular when issues of interest were mentioned and where.
#  - Returning all the examples of these things being mentioned.
# 
# ## Notes:  Ensure AnythingLLM is running on a docker instance: /usr/local/bin/docker-compose up -d --build
# 
# ## Remember, we need to have a persistent terminal running the following command that watches for file uploads:
# ## sudo docker exec -it --workdir=/app/collector anything-llm python watch.py
# 
# # TODO: 
# The core algorithm should expect something like :
# A title to use to describe this thing (like "Cost Concerns" or "competitor - snowflake" or whatever)
# A list of strings corresponding to the thing (like ['this might be too expensive,' 'can we talk about overall cost, ...'])
# A switch for determining if this is meant to be an exact match to some of this stuff or if we're trying to match the overall concept/fuzzy-match
# An optional time frame to look for a second group in, to be delivered along with this one.
# And then basically to return an object where we can get all the examples of the concept happening....
# So do the following:
#  - set up a json object for input, make a bunch of examples
#  - make a nice csv file from parsing all the input files.
#  - make a get_fuzzy function that gets all mentions, regexes those back out of the summary file and returns all the examples
#  - make a get_exact function that does the same with regex. In both, return an object with a count and a set of stuff (can we add time?)
#  - make an answer_questions manifold function that goes through as many questions as you have and returns a json object (or gives up) for each question/key.

# %%
from transcript_helpers import TranscriptEmbedder
import json
import os
import re

import requests
import json

import shutil

# where the text files are
anythingllm_summarydir = '/home/frog/repos/latest-anything-llm'
# where AnythingLLM is installed
anythingllm_rootdir = '/home/frog/repos/anything-llm'

# the new domain name to construct
tenant_name = 'test_aaron_text'
# files we'd like to include in this new domain
#files_to_encode = ['Aaron_McCloud_Resume_13-web-dev-for-MUI.pdf']
files_to_encode = ['aaron_test.txt']




# %% [markdown]
# ## Remember, we need to have a persistent terminal running the following command that watches for file uploads:
# ## sudo docker exec -it --workdir=/app/collector anything-llm python watch.py

# %%
embedded_documents = TranscriptEmbedder()

# To set this up the first time
embedded_documents.set_up_by_filelist(files_to_encode,tenant_name,anythingllm_summarydir,anythingllm_rootdir)

# Subsequent times we'd like to address this person/tenant/domain again:
#embedded_documents.set_up_by_domain_name(tenant_name,anythingllm_summarydir,anythingllm_rootdir)


# %% [markdown]
# # Test Queries

# %%
embedded_documents.return_fuzzy_mentions('front end systems')



