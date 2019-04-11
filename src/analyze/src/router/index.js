import Vue from 'vue';
import Router from 'vue-router';
import Repo from '@/views/Repo';
import Projects from '@/views/Projects';
import store from '@/store/';
import Start from '@/views/Start';
import Design from '@/views/Design';
import Dashboards from '@/views/Dashboards';
import Settings from '@/views/Settings';
import ConnectorsPage from '@/views/ConnectorsPage';
import SettingsDatabase from '@/components/settings/Database';
import SettingsRoles from '@/components/settings/Roles';

Vue.use(Router);

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: '/projects',
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
      path: '/projects/:projectSlug/files/',
      name: 'projectFiles',
      component: Repo,
    },
    {
      path: '/projects/:projectSlug/analyze/:model/:design',
      name: 'analyze',
      component: Design,
    },
    {
      path: '/projects/:projectSlug/analyze/:model/:design/reports/report/:slug',
      name: 'design_report',
      component: Design,
    },
    {
      path: '/projects/:projectSlug/dashboards/',
      name: 'dashboards',
      component: Dashboards,
    },
    {
      path: '/projects/:projectSlug/dashboards/dashboard/:slug',
      name: 'dashboard',
      component: Dashboards,
    },
    {
      path: '/projects/:projectSlug/settings',
      name: 'settings',
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
          component: ConnectorsPage,
        },
      ],
    },
  ],
});

// Update project at global level vs in each page/view component where subsequent API calls can
// leverage the project store's `currentProjectSlug` for prefixing API calls with a project context
router.beforeEach((to, from, next) => {
  const projectSlug = to.params.projectSlug || '';
  store.dispatch('projects/setProjectSlug', projectSlug);
  next();
});

export default router;
