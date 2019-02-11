import Vue from 'vue';
import Router from 'vue-router';
import Repo from '@/views/Repo';
import Design from '@/views/Design';
import Dashboards from '@/views/Dashboards';
import Settings from '@/views/Settings';
import Orchestrate from '@/views/Orchestrate';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
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
      path: '/design/:model/:design',
      name: '',
      component: Design,
    },
    {
      path: '/dashboards/',
      name: 'Dashboards',
      component: Dashboards,
    },
    {
      path: '/dashboards/:id',
      name: 'Dashboards',
      component: Dashboards,
    },
    {
      path: '/settings',
      name: '',
      component: Settings,
    },
    {
      path: '/orchestrations',
      name: 'Orchestrate',
      component: Orchestrate,
    },
  ],
});
