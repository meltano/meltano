import Router from 'vue-router';
import Vue from 'vue';

import DataSetup from '@/views/DataSetup';
import Design from '@/views/Design';
import Designs from '@/views/Designs';
import Dashboards from '@/views/Dashboards';
import NotFound from '@/views/NotFound';
import Orchestration from '@/views/Orchestration';
import Repo from '@/views/Repo';
import Transformations from '@/views/Transformations';

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
      redirect: '/configuration',
    },
    {
      path: '/configuration/',
      name: 'dataSetup',
      component: DataSetup,
    },
    {
      path: '/transformations/',
      name: 'transformations',
      component: Transformations,
    },
    {
      path: '/orchestration/',
      name: 'orchestration',
      component: Orchestration,
    },
    {
      path: '/files/',
      name: 'projectFiles',
      component: Repo,
    },
    {
      path: '/analyze/',
      name: 'analyze',
      component: Designs,
    },
    {
      path: '/analyze/:model/:design',
      name: 'analyze_design',
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
  ],
});

export default router;
