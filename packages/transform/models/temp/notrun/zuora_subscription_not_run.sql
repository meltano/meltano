SELECT 1
/*SELECT sa.id as SFDC_accountid,
	     pa.id as SFDC_parentaccountId,
	     s.id as subscriptionid,
       s.accountid as billingaccountid,
       s.autorenew,
       s.cancelleddate,
       s.contracteffectivedate,
       s.currentterm,
       s.currenttermperiodtype,
       s.initialterm,
       s.initialtermperiodtype,
       s.invoiceownerid,
       s.isinvoiceseparate,
       s.purchase_order__c,
       s.name as subscription_name,
       s.originalid as original_subscription_id,
       s.previoussubscriptionid,
       s.purchaseorder__c,
       s.clickthrougheularequired__c,
       s.renewalterm,
       s.renewaltermperiodtype,
       s.status,
       s.subscriptionenddate,
       s.subscriptionstartdate,
       s.termenddate,
       s.termstartdate,
       s.termtype,
       s.updateddate,
       s.VERSION as subscriptionversion,
	     c.effectivestartdate,
       c.effectiveenddate,
       c.mrr,
       c.mrr * 12::numeric AS arr,
       c.billingperiod,
       p.id as productid,
       c.quantity,
       c.uom,
       c.tcv
FROM zuora.subscription s
JOIN zuora.account a ON s.accountid = a.id::text
     JOIN zuora.rateplan r ON r.subscriptionid::text = s.id
     JOIN zuora.rateplancharge c ON c.rateplanid::text = r.id::text
     JOIN sfdc.z_billingaccount ba ON a.id::text = ba.zuora__zuora_id__c
     JOIN sfdc.account sa ON ba.zuora__account__c = sa.id::text
     JOIN sfdc.account pa ON sfdc.id15to18("substring"(sa.ultimate_parent_account__c, 11, 15)) = pa.id::text
	 JOIN zuora.productrateplan pr on r.productrateplanid=pr.id
	 JOIN zuora.product p on pr.productid=p.id
where (excludefromanalysis__c is null or excludefromanalysis__c=false) and s.status<>'Expired' */