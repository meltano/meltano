SELECT c.id,
           q.opportunity_id__c AS opportunity_id,
           c.zqu__rateplanname__c AS product,
           c.zqu__period__c AS period,
           c.zqu__quantity__c AS qty,
           CASE WHEN  sum(COALESCE(c.zqu__billingsubtotal__c, c.zqu__total__c)) OVER (PARTITION BY q.id) = 0 THEN 0 ELSE 
           round((o.Incremental_ACV__c * (COALESCE(c.zqu__billingsubtotal__c, c.zqu__total__c) / sum(COALESCE(c.zqu__billingsubtotal__c, c.zqu__total__c)) OVER (PARTITION BY q.id)))::numeric, 4) END AS iacv,
           CASE WHEN  sum(COALESCE(c.zqu__billingsubtotal__c, c.zqu__total__c)) OVER (PARTITION BY q.id) = 0 THEN 0 ELSE 
           round((o.ACV__c * (COALESCE(c.zqu__billingsubtotal__c, c.zqu__total__c) / sum(COALESCE(c.zqu__billingsubtotal__c, c.zqu__total__c)) OVER (PARTITION BY q.id)))::numeric, 4) END AS acv,
           CASE WHEN  sum(COALESCE(c.zqu__billingsubtotal__c, c.zqu__total__c)) OVER (PARTITION BY q.id) = 0 THEN 0 ELSE 
           round((o.Renewal_ACV__c * (COALESCE(c.zqu__billingsubtotal__c, c.zqu__total__c) / sum(COALESCE(c.zqu__billingsubtotal__c, c.zqu__total__c)) OVER (PARTITION BY q.id)))::numeric, 4) END AS renewal_acv,
           CASE WHEN  sum(COALESCE(c.zqu__billingsubtotal__c, c.zqu__total__c)) OVER (PARTITION BY q.id) = 0 THEN 0 ELSE 
           round((o.Amount * (COALESCE(c.zqu__billingsubtotal__c, c.zqu__total__c) / sum(COALESCE(c.zqu__billingsubtotal__c, c.zqu__total__c)) OVER (PARTITION BY q.id)))::numeric, 4) END AS tcv
   FROM sfdc.zqu__quote__c q
    JOIN sfdc.zqu__quoterateplan__c r ON r.zqu__quote__c = q.id
    JOIN sfdc.zqu__quoterateplancharge__c c ON c.zqu__quoterateplan__c = r.id
    JOIN sfdc.zqu__productrateplan__c pr ON r.zqu__productrateplan__c = pr.id
    JOIN sfdc.zqu__zproduct__c p ON pr.zqu__zproduct__c = p.id
    JOIN sfdc.opportunity o ON q.opportunity_id__c = o.id::text
    WHERE q.isdeleted = FALSE
      AND r.isdeleted = FALSE
      AND c.isdeleted = FALSE
      AND o.isdeleted = FALSE
      AND q.zqu__primary__c = TRUE
