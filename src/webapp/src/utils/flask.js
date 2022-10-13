/*
   This module handles the Flask context,
   either set by the Meltano API in production
   or from webpack in development.
*/

export default function () {
  return (
    window.FLASK || {
      appUrl: process.env.MELTANO_APP_URL,
      oauthServiceUrl: process.env.MELTANO_OAUTH_SERVICE_URL || null,
      oauthServiceProviders: (process.env.MELTANO_OAUTH_SERVICE_PROVIDERS || '')
        .split(',')
        .filter(Boolean),
      isAnalysisEnabled: true,
      isNotificationEnabled: false,
      isProjectReadonlyEnabled: false,
      isReadonlyEnabled: false,
      isAnonymousReadonlyEnabled: false,
      isSendAnonymousUsageStats: false,
      projectId: 'none',
      version: 'source',
    }
  )
}
