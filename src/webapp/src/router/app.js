import Router from 'vue-router'

import Design from '@/components/analyze/Design'
import Explore from '@/components/analyze/Explore'
import CreatePipelineScheduleModal from '@/components/pipelines/CreatePipelineScheduleModal'
import EditPipelineScheduleModal from '@/components/pipelines/EditPipelineScheduleModal'
import LogModal from '@/components/pipelines/LogModal'
import PluginSettingsModal from '@/components/pipelines/PluginSettingsModal'

import Analyze from '@/views/Analyze'
import Dashboard from '@/views/Dashboard'
import Dashboards from '@/views/Dashboards'
import NotFound from '@/views/NotFound'
import Pipelines from '@/views/Pipelines'
import Plugins from '@/views/Plugins'

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
      redirect: '/extractors'
    },
    {
      path: '/extractors/',
      name: 'extractors',
      component: Plugins,
      props: { pluginType: 'extractors' },
      children: [
        {
          path: ':plugin',
          name: 'extractorSettings',
          components: {
            default: Plugins,
            extractorSettings: PluginSettingsModal
          },
          props: { extractorSettings: { pluginType: 'extractors' } },
          meta: {
            isModal: true,
            title: 'Meltano: Data Extractor Configuration'
          }
        }
      ]
    },
    {
      path: '/loaders/',
      name: 'loaders',
      component: Plugins,
      props: { pluginType: 'loaders' },
      children: [
        {
          path: ':plugin',
          name: 'loaderSettings',
          components: {
            default: Plugins,
            loaderSettings: PluginSettingsModal
          },
          props: { loaderSettings: { pluginType: 'loaders' } },
          meta: {
            isModal: true,
            title: 'Meltano: Data Loader Configuration'
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
          path: 'create',
          name: 'createPipelineSchedule',
          components: {
            default: Pipelines,
            createPipelineSchedule: CreatePipelineScheduleModal
          },
          meta: {
            isModal: true,
            title: 'Meltano: Create pipelines'
          }
        },
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
        },
        {
          path: 'edit-pipeline-schedule/:jobId',
          name: 'editPipelineSchedule',
          components: {
            default: Pipelines,
            editPipelineSchedule: EditPipelineScheduleModal
          },
          meta: {
            isModal: true,
            title: 'Meltano: Edit pipelines'
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
