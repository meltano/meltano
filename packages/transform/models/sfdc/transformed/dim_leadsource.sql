{{
  config({
    "materialized":"table",
    "post-hook": [
       "ALTER TABLE {{ this }} ADD PRIMARY KEY(id)"
    ]
  })
}}

with leadsource as (
		select * from {{ ref('leadsource') }}
)

SELECT  row_number() OVER (
                          ORDER BY LeadSource) AS id
        , COALESCE(LeadSource, 'Unknown') as Initial_Source
        , CASE WHEN LeadSource IN('Advertisement')
        		THEN 'Advertising'
        	   WHEN LeadSource IN('Email Request', 'Email Subscription', 'Newsletter', 'Security Newsletter')
        	    THEN 'Email'
        	   WHEN LeadSource IN('Live Event', 'Trade Show', 'Confernece', 'Seminar - Partner', 'Seminar - Internal')
        	    THEN 'Events'
        	   WHEN LeadSource IN('Contact Request', 'Enterprise Trial', 'Development Request', 'Prof Serv Request', 'Web', 'Webcast', 'Web Chat', 'Web Direct', 'White Paper', 'Training Request', 'Consultancy Request', 'Public Relations')
        	    THEN 'Marketing Site'
        	   WHEN LeadSource IN('SDR Generated', 'Linkedin', 'LeadWare', 'AE Generated', 'Datanyze', 'DiscoverOrg', 'Clearbit')
        	    THEN 'Prospecting'
        	   WHEN LeadSource IN('Gitorious', 'GitLab Hosted', 'GitLab EE instance', 'GitLab.com', 'CE Download', 'CE Usage Ping')
        	    THEN 'Product'
        	   WHEN LeadSource IN('Word of Mouth', 'External Referral', 'Employee Referral', 'Partner', 'Existing Client')
        	    THEN 'Referral'
        	   ELSE 'Other'
          END as Initial_Source_Type  
FROM leadsource