import Vue from 'vue';
import Router from 'vue-router';
import Repo from '@/views/Repo';
import Design from '@/views/Design';
import Dashboards from '@/views/Dashboards';
import NotFound from '@/views/NotFound';
import Settings from '@/views/Settings';
import Connectors from '@/views/Connectors';
import SettingsDatabase from '@/components/settings/Database';
import SettingsRoles from '@/components/settings/Roles';

Vue.use(Router);

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '*',
      name: '404',
      component: NotFound,
    },
    {
      path: '/',
      redirect: '/files',
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
      children: [
        {
          path: 'roles',
          name: 'roles',
          component: SettingsRoles,
        },
        {
          path: 'database',
          name: 'database',
          component: SettingsDatabase,
        },
        {
          path: 'connectors',
          name: 'connectors',
          component: Connectors,
        },
      ],
    },
  ],
});

export default router;
