import Vue from 'vue';
import Router from 'vue-router';
import Repo from '@/views/Repo';
import Start from '@/views/Start';
import Design from '@/views/Design';
import Dashboards from '@/views/Dashboards';
import Orchestrate from '@/views/Orchestrate';
import Settings from '@/views/Settings';
import SettingsDatabase from '@/components/settings/Database';
import SettingsRoles from '@/components/settings/Roles';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      redirect: '/files',
    },
    {
      path: '/start/',
      name: 'Start',
      component: Start,
    },
    {
      path: '/files/',
      name: 'Repo',
      component: Repo,
    },
    {
      path: '/analyze/:model/:design',
      name: '',
      component: Design,
    },
    {
      path: '/analyze/:model/:design/reports/report/:slug',
      name: 'Report',
      component: Design,
    },
    {
      path: '/dashboards/',
      name: 'Dashboards',
      component: Dashboards,
    },
    {
      path: '/dashboards/dashboard/:slug',
      name: 'Dashboard',
      component: Dashboards,
    },
    {
      path: '/settings',
      name: 'Settings',
      component: Settings,
      children: [{
        path: 'roles',
        component: SettingsRoles,
      }, {
        path: 'database',
        component: SettingsDatabase,
      }],
    },
    {
      path: '/orchestrations',
      name: 'Orchestrate',
      component: Orchestrate,
    },
  ],
});
