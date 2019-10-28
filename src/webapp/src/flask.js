/*
   This module handles the Flask context,
   either set by the Meltano API in production
   or from webpack in development.
*/

module.exports = function() {
  return (
    window.FLASK || {
      airflowUrl: process.env.AIRFLOW_URL,
      appUrl: process.env.MELTANO_WEBAPP_URL,
      dbtDocsUrl: process.env.DBT_DOCS_URL,
      isSendAnonymousUsageStats: false,
      projectId: 'none',
      version: 'source'
    }
  )
}
