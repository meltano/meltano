import Router from 'vue-router'

import ReportEmbed from '@/views/ReportEmbed'

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/-/embed/:token',
      name: 'report-embed',
      component: ReportEmbed,
      meta: {
        title: 'Meltano Report Embed'
      },
      props: true
    }
  ]
})

export default router
