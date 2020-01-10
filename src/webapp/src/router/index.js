import Router from 'vue-router'

import CreatePipelineScheduleModal from '@/components/pipelines/CreatePipelineScheduleModal'
import Design from '@/components/analyze/Design'
import Extractors from '@/components/pipelines/Extractors'
import ExtractorSettingsModal from '@/components/pipelines/ExtractorSettingsModal'
import Loaders from '@/components/pipelines/Loaders'
import LoaderSettingsModal from '@/components/pipelines/LoaderSettingsModal'
import LogModal from '@/components/pipelines/LogModal'
import PipelineSchedules from '@/components/pipelines/PipelineSchedules'

import Analyze from '@/views/Analyze'
import Dashboards from '@/views/Dashboards'
import Dashboard from '@/views/Dashboard'
import NotFound from '@/views/NotFound'
import Pipelines from '@/views/Pipelines'

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
      redirect: '/pipeline'
    },
    {
      path: '/pipeline/',
      redirect: '/pipeline/extract/',
      name: 'dataSetup',
      component: Pipelines,
      children: [
        {
          path: 'extract',
          name: 'extractors',
          components: {
            default: Extractors
          },
          meta: {
            isModal: false,
            title: 'Meltano: Pipeline - Extract'
          }
        },
        {
          path: 'extract/:extractor/configure',
          name: 'extractorSettings',
          components: {
            default: Extractors,
            extractorSettings: ExtractorSettingsModal
          },
          meta: {
            isModal: true,
            title: 'Meltano: Pipeline - Extractor Configuration'
          }
        },
        {
          path: 'load',
          name: 'loaders',
          components: {
            default: Loaders
          },
          meta: {
            isModal: false,
            title: 'Meltano: Pipeline - Load'
          }
        },
        {
          path: 'load/:loader',
          name: 'loaderSettings',
          components: {
            default: Loaders,
            loaderSettings: LoaderSettingsModal
          },
          meta: {
            isModal: true,
            title: 'Meltano: Pipeline - Loader Settings'
          }
        },
        {
          path: 'schedule',
          name: 'schedules',
          components: {
            default: PipelineSchedules
          },
          meta: {
            isModal: false,
            title: 'Meltano: Pipeline - Schedule'
          }
        },
        {
          path: 'schedule/create',
          name: 'createPipelineSchedule',
          components: {
            default: PipelineSchedules,
            createPipelineSchedule: CreatePipelineScheduleModal
          },
          meta: {
            isModal: true,
            title: 'Meltano: Pipeline - Create Schedule'
          }
        },
        {
          path: 'schedule/log/:jobId',
          name: 'runLog',
          components: {
            default: PipelineSchedules,
            runLog: LogModal
          },
          meta: {
            isModal: true,
            title: 'Meltano: Pipeline - Run Log'
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
