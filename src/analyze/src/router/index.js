import Vue from 'vue';
import Router from 'vue-router';
import Repo from '@/views/Repo';
import Projects from '@/views/Projects';
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
      name: 'files',
      redirect: '/files',
    },
    {
      path: '/projects/',
      name: 'projects',
      component: Projects,
    },
    {
      path: '/start/',
      name: 'start',
      component: Start,
    },
    {
      path: '/projects/:slug/files/',
      name: 'projectFiles',
      component: Repo,
    },
    {
      path: '/analyze/:model/:design',
      name: '',
      component: Design,
    },
    {
      path: '/analyze/:model/:design/reports/report/:slug',
      name: 'design_report',
      component: Design,
    },
    {
      path: '/dashboards/',
      name: 'dashboards',
      component: Dashboards,
    },
    {
      path: '/dashboards/dashboard/:slug',
      name: 'dashboard',
      component: Dashboards,
    },
    {
      path: '/settings',
      name: 'settings',
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
      name: 'orchestrate',
      component: Orchestrate,
    },
  ],
});
