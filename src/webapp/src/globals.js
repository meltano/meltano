/*
   This module is a shim to inject globals
   variable in the development version of
   the UI.

   In production, these variavbles will be
   set in the template by Flask.
*/

module.exports = {
  appUrl: process.env.MELTANO_WEB_APP_URL,
  airflowUrl: process.env.AIRFLOW_URL
}
