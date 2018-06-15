import Vue from 'vue';
import Router from 'vue-router';
import Project from '@/components/projects/Project';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Project',
      component: Project,
    },
  ],
});
