import Router from 'vue-router'

import Design from '@/components/analyze/Design'
import ExtractorSettingsModal from '@/components/pipelines/ExtractorSettingsModal'
import LogModal from '@/components/pipelines/LogModal'

import Analyze from '@/views/Analyze'
import Dashboards from '@/views/Dashboards'
import Dashboard from '@/views/Dashboard'
import Datasets from '@/views/Datasets'
import NotFound from '@/views/NotFound'

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '*',
      name: '404',
      component: NotFound,
      meta: {
        title: 'Meltano: Not Found'
      }
    },
    {
      path: '/',
      redirect: '/data'
    },
    {
      path: '/data/',
      name: 'datasets',
      component: Datasets,
      children: [
        {
          path: 'extract/:extractor',
          name: 'extractorSettings',
          components: {
            default: Datasets,
            extractorSettings: ExtractorSettingsModal
          },
          meta: {
            isModal: true,
            title: 'Meltano: Data Extractor Configuration'
          }
        },
        {
          path: 'schedule/:jobId',
          name: 'runLog',
          components: {
            default: Datasets,
            runLog: LogModal
          },
          meta: {
            isModal: true,
            title: 'Meltano: Job Log'
          }
        }
      ]
    },
    {
      path: '/analyze/',
      name: 'analyze',
      component: Analyze,
      meta: {
        title: 'Meltano: Analyze'
      },
      children: [
        {
          path: '/analyze/:namespace+/:model/:design/reports/:slug',
          name: 'report',
          component: Design,
          meta: {
            title: 'Meltano: Analyze - Report'
          }
        },
        {
          path: '/analyze/:namespace+/:model/:design',
          name: 'analyzeDesign',
          component: Design,
          meta: {
            title: 'Meltano: Analyze - Model Design'
          }
        }
      ]
    },
    {
      path: '/dashboards/',
      name: 'dashboards',
      component: Dashboards,
      meta: {
        title: 'Meltano: Dashboards'
      }
    },
    {
      path: '/dashboards/:slug',
      name: 'dashboard',
      component: Dashboard,
      meta: {
        title: 'Meltano: Dashboard'
      }
    }
  ]
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'Meltano'
  next()
})

export default router
