import Router from 'vue-router'

import Design from '@/components/analyze/Design'
import Explore from '@/components/analyze/Explore'
import ExtractorSettingsModal from '@/components/pipelines/ExtractorSettingsModal'
import LogModal from '@/components/pipelines/LogModal'

import Analyze from '@/views/Analyze'
import Dashboards from '@/views/Dashboards'
import Dashboard from '@/views/Dashboard'
import DataSources from '@/views/DataSources'
import Pipelines from '@/views/Pipelines'
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
      redirect: '/data-sources'
    },
    {
      path: '/data-sources/',
      name: 'data-sources',
      component: DataSources,
      children: [
        {
          path: ':extractor',
          name: 'extractorSettings',
          components: {
            default: DataSources,
            extractorSettings: ExtractorSettingsModal
          },
          meta: {
            isModal: true,
            title: 'Meltano: Data Extractor Configuration'
          }
        }
      ]
    },
    {
      path: '/pipelines/',
      name: 'pipelines',
      component: Pipelines,
      children: [
        {
          path: ':jobId',
          name: 'runLog',
          components: {
            default: Pipelines,
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
          path: '/analyze/:extractor',
          name: 'explore',
          component: Explore,
          meta: {
            title: 'Meltano: Analyze - Explore'
          }
        },
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
          name: 'design',
          component: Design,
          meta: {
            title: 'Meltano: Analyze - Report Builder'
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
