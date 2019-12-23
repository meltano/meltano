/*
   This module handles the Flask context,
   either set by the Meltano API in production
   or from webpack in development.
*/

module.exports = function() {
  return (
    window.FLASK || {
      appUrl: process.env.MELTANO_APP_URL,
      dbtDocsUrl: process.env.DBT_DOCS_URL,
      isSendAnonymousUsageStats: false,
      projectId: 'none',
      version: 'source'
    }
  )
}
