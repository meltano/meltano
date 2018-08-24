SELECT distinct LeadSource from sfdc.opportunity where isdeleted='false' and LeadSource is not null
UNION  
SELECT distinct LeadSource from sfdc.lead where isdeleted='false' and LeadSource is not null
UNION
SELECT distinct LeadSource from sfdc.contact where isdeleted='false' and LeadSource is not null