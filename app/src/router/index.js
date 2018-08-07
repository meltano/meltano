import Vue from 'vue';
import Router from 'vue-router';
import Project from '@/components/projects/Project';
import NewProjectForm from '@/components/projects/NewProjectForm';
import Repo from '@/components/repos/Repo';
import Explore from '@/components/explores/Explore';
import Settings from '@/components/settings/Settings';
import Orchestrate from '@/components/orchestrations/Orchestrate';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      redirect: '/project',
    },
    {
      path: '/project',
      name: 'Project',
      component: Project,
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
      path: '/explore/:model/:explore',
      name: '',
      component: Explore,
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
