SELECT a.id AS sfdc_account_id,
       a.name,
       a.industry,
       a.TYPE,
       a.Sales_Segmentation__c,
       {{this.schema}}.id15to18(substring(a.ultimate_parent_account__c,11, 15)) AS ultimate_parent_account__c,
       p.Sales_Segmentation__c AS ultimate_parent_Sales_Segmentation,
       p.name AS ultimate_parent_name,
       CASE
           WHEN p.Sales_Segmentation__c IN('Large', 'Strategic')
                OR a.Sales_Segmentation__c IN('Large', 'Strategic') THEN TRUE
           ELSE FALSE
       END AS Is_LAU,
       a.health__c as health_score,
       a.health_score_reasons__c as health_score_reasons,
       u.name as technical_account_manager,
       a.sales_segmentation_new__c as new_sales_segmentation,
       a.number_of_open_opportunities__c as count_open_opportunities
FROM sfdc.account a
LEFT OUTER JOIN sfdc.account p ON {{this.schema}}.id15to18(substring(a.ultimate_parent_account__c,11, 15))=p.id
LEFT OUTER JOIN sfdc.user u on u.id = a.technical_account_manager_lu__c
WHERE a.isdeleted=FALSE