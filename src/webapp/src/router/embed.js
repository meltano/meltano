import Router from 'vue-router'

import ReportEmbed from '@/components/embed/ReportEmbed'

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'report-embed',
      component: ReportEmbed,
      meta: {
        title: 'Meltano Report Embed'
      }
    }
  ]
})

export default router
