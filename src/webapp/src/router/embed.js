import Router from 'vue-router'

import ResourceEmbed from '@/views/ResourceEmbed'

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/-/embed/:token',
      name: 'resource-embed',
      component: ResourceEmbed,
      meta: {
        title: 'Meltano Resource Embed'
      },
      props: true
    }
  ]
})

export default router
