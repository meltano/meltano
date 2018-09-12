with ss_opportunity as (

       SELECT *
       FROM sfdc_derived.ss_opportunity
       WHERE isdeleted=FALSE

)

SELECT id AS sfdc_opportunity_id,
       snapshot_date,
       accountid,
       stagename,
       leadsource,
       TYPE,
       closedate,
       sql_source__c,
       sales_segmentation_o__c,
       sales_qualified_date__c,
       sales_accepted_date__c,
       reason_for_lost__c as reason_for_loss,
       reason_for_lost_details__c as reason_for_loss_details,
       name,
       ownerid,
       Incremental_ACV__c AS iacv,
       ACV__c as ACV,
       Renewal_ACV__c as Renewal_ACV,
       Amount as TCV
       
FROM ss_opportunity

