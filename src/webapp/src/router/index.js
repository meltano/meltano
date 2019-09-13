import Router from 'vue-router'

import AnalyzeModels from '@/components/analyze/AnalyzeModels'
import AnalyzeSettings from '@/components/analyze/AnalyzeSettings'
import AnalyzeConnectionSettingsModal from '@/components/analyze/AnalyzeConnectionSettingsModal'
import CreateScheduleModal from '@/components/pipelines/CreateScheduleModal'
import Design from '@/components/analyze/Design'
import EntitiesSelectorModal from '@/components/pipelines/EntitiesSelectorModal'
import Extractors from '@/components/pipelines/Extractors'
import ExtractorSettingsModal from '@/components/pipelines/ExtractorSettingsModal'
import Loaders from '@/components/pipelines/Loaders'
import LoaderSettingsModal from '@/components/pipelines/LoaderSettingsModal'
import PipelineSchedules from '@/components/pipelines/PipelineSchedules'
import Transforms from '@/components/pipelines/Transforms'

import Analyze from '@/views/Analyze'
import Dashboards from '@/views/Dashboards'
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
      redirect: '/pipelines'
    },
    {
      path: '/pipelines/',
      redirect: '/pipelines/extractors/',
      name: 'dataSetup',
      component: Pipelines,
      children: [
        {
          path: 'extractors',
          name: 'extractors',
          components: {
            default: Extractors
          },
          meta: {
            isModal: false,
            title: 'Meltano: Pipelines - Extractors'
          }
        },
        {
          path: 'extractors/:extractor/configure',
          name: 'extractorSettings',
          components: {
            default: Extractors,
            extractorSettings: ExtractorSettingsModal
          },
          meta: {
            isModal: true,
            title: 'Meltano: Pipelines - Extractor Configuration'
          }
        },
        {
          path: 'extractors/:extractor/select',
          name: 'extractorEntities',
          components: {
            default: Extractors,
            extractorEntities: EntitiesSelectorModal
          },
          meta: {
            isModal: true,
            title: 'Meltano: Pipelines - Extractor Entities'
          }
        },
        {
          path: 'loaders',
          name: 'loaders',
          components: {
            default: Loaders
          },
          meta: {
            isModal: false,
            title: 'Meltano: Pipelines - Loaders'
          }
        },
        {
          path: 'loaders/:loader',
          name: 'loaderSettings',
          components: {
            default: Loaders,
            loaderSettings: LoaderSettingsModal
          },
          meta: {
            isModal: true,
            title: 'Meltano: Pipelines - Loader Settings'
          }
        },
        {
          path: 'transforms',
          name: 'transforms',
          components: {
            default: Transforms
          },
          meta: {
            isModal: false,
            title: 'Meltano: Pipelines - Transforms'
          }
        },
        {
          path: 'schedules',
          name: 'schedules',
          components: {
            default: PipelineSchedules
          },
          meta: {
            isModal: false,
            title: 'Meltano: Pipelines - Schedules'
          }
        },
        {
          path: 'schedules/create',
          name: 'createSchedule',
          components: {
            default: PipelineSchedules,
            createSchedule: CreateScheduleModal
          },
          meta: {
            isModal: true,
            title: 'Meltano: Pipelines - Create Schedules'
          }
        }
      ]
    },
    {
      path: '/orchestration/',
      name: 'orchestration',
      component: Orchestration,
      meta: {
        title: 'Meltano: Orchestration'
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
          path: 'models',
          name: 'analyzeModels',
          component: AnalyzeModels,
          meta: {
            title: 'Meltano: Analyze - Models'
          }
        },
        {
          path: 'settings',
          name: 'analyzeSettings',
          component: AnalyzeSettings,
          meta: {
            title: 'Meltano: Analyze - Settings'
          }
        },
        {
          path: 'settings/:connector',
          name: 'analyzeConnectionSettings',
          components: {
            default: AnalyzeSettings,
            analyzeConnectionSettings: AnalyzeConnectionSettingsModal
          },
          meta: {
            isModal: true,
            title: 'Meltano: Analyze - Connector Settings'
          }
        },
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
      path: '/dashboards/',
      name: 'dashboards',
      component: Dashboards,
      meta: {
        title: 'Meltano: Dashboards'
      }
    },
    {
      path: '/dashboards/dashboard/:slug',
      name: 'dashboard',
      component: Dashboards,
      meta: {
        title: 'Meltano: Dashboards'
      }
    }
  ]
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'Meltano'
  next()
})

export default router
