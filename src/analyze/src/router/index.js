import Vue from 'vue';
import Router from 'vue-router';
import NewProjectForm from '@/components/projects/NewProjectForm';
import Repo from '@/components/repos/Repo';
import Design from '@/components/designs/Design';
import Dashboards from '@/components/dashboards/Dashboards';
import Settings from '@/components/settings/Main';
import SettingsDatabase from '@/components/settings/Database';
import SettingsRoles from '@/components/settings/Roles';
import Extract from '@/components/extract/Extract';
import Load from '@/components/load/Load';
import Transform from '@/components/transform/Transform';
import Orchestrate from '@/components/orchestrations/Orchestrate';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      redirect: '/model',
    },
    {
      path: '/extract',
      name: 'Extract',
      component: Extract,
    },
    {
      path: '/load',
      name: 'Load',
      component: Load,
    },
    {
      path: '/transform',
      name: 'Transform',
      component: Transform,
    },
    {
      path: '/project/new',
      name: 'NewProjectForm',
      component: NewProjectForm,
    },
    {
      path: '/repo/',
      name: 'Repo',
      component: Repo,
    },
    {
      path: '/model/',
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
