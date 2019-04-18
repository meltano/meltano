import Router from 'vue-router';
import Vue from 'vue';

import store from '@/store/';

import DataSetup from '@/views/DataSetup';
import Design from '@/views/Design';
import Designs from '@/views/Designs';
import Dashboards from '@/views/Dashboards';
import NotFound from '@/views/NotFound';
import Orchestration from '@/views/Orchestration';
import Projects from '@/views/Projects';
import Repo from '@/views/Repo';
import Start from '@/views/Start';
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
      path: '/projects/:projectSlug/setup/',
      name: 'dataSetup',
      component: DataSetup,
    },
    {
      path: '/projects/:projectSlug/transformations/',
      name: 'transformations',
      component: Transformations,
    },
    {
      path: '/projects/:projectSlug/orchestration/',
      name: 'orchestration',
      component: Orchestration,
    },
    {
      path: '/projects/:projectSlug/files/',
      name: 'projectFiles',
      component: Repo,
    },
    {
      path: '/projects/:projectSlug/analyze/',
      name: 'analyze',
      component: Designs,
    },
    {
      path: '/projects/:projectSlug/analyze/:model/:design',
      name: 'analyze_design',
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
