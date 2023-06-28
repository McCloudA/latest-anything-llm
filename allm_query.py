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

# TODO: 
# look through existing db applcant stuff, figur eout what's still missing
# make a series of query pieces thast should give us our stuff (address?, skills, websites etc. ).  
# make a series of attempted json functions, try 3 times for each thing.  default out to just no record for jobs, and something basic for skills"
# make a set of queries to look for missing pieces from records, make them, add them.
# test.

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