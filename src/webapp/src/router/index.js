import Router from 'vue-router'

import CreateScheduleModal from '@/components/pipelines/CreateScheduleModal'
import Design from '@/components/analyze/Design'
import EntitiesSelectorModal from '@/components/pipelines/EntitiesSelectorModal'
import Extractors from '@/components/pipelines/Extractors'
import ExtractorSettingsModal from '@/components/pipelines/ExtractorSettingsModal'
import Loaders from '@/components/pipelines/Loaders'
import LoaderSettingsModal from '@/components/pipelines/LoaderSettingsModal'
import LogModal from '@/components/pipelines/LogModal'
import PipelineSchedules from '@/components/pipelines/PipelineSchedules'
import Transforms from '@/components/pipelines/Transforms'

import Analyze from '@/views/Analyze'
import Dashboards from '@/views/Dashboards'
import Model from '@/views/Model'
import NotFound from '@/views/NotFound'
import Orchestration from '@/views/Orchestration'
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
          path: 'extract/:extractor/select',
          name: 'extractorEntities',
          components: {
            default: Extractors,
            extractorEntities: EntitiesSelectorModal
          },
          meta: {
            isModal: true,
            title: 'Meltano: Pipeline - Extractor Entities'
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
          path: 'transform',
          name: 'transforms',
          components: {
            default: Transforms
          },
          meta: {
            isModal: false,
            title: 'Meltano: Pipeline - Transform'
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
          name: 'createSchedule',
          components: {
            default: PipelineSchedules,
            createSchedule: CreateScheduleModal
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
      path: '/orchestrate/',
      name: 'orchestration',
      component: Orchestration,
      meta: {
        title: 'Meltano: Orchestration'
      }
    },
    {
      path: '/model/',
      name: 'model',
      component: Model,
      meta: {
        title: 'Meltano: Model'
      }
    },
    {
      path: '/analyze/',
      redirect: '/analyze/models/',
      name: 'analyze',
      component: Analyze,
      meta: {
        title: 'Meltano: Analyze'
      },
      children: [
        {
          path: '/analyze/:namespace+/:model/:design',
          name: 'analyzeDesign',
          component: Design,
          meta: {
            title: 'Meltano: Analyze - Model Design'
          }
        },
        {
          path: '/analyze/:namespace+/:model/:design/reports/report/:slug',
          name: 'report',
          component: Design,
          meta: {
            title: 'Meltano: Analyze - Reports'
          }
        }
      ]
    },
    {
      path: '/dashboard/',
      name: 'dashboards',
      component: Dashboards,
      meta: {
        title: 'Meltano: Dashboard'
      }
    },
    {
      path: '/dashboard/:slug',
      name: 'dashboard',
      component: Dashboards,
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
