import Router from 'vue-router'

import AnalyzeModels from '@/components/analyze/AnalyzeModels'
import AnalyzeSettings from '@/components/analyze/AnalyzeSettings'
import CreateScheduleModal from '@/components/pipelines/CreateScheduleModal'
import Design from '@/components/analyze/Design'
import EntitiesSelectorModal from '@/components/pipelines/EntitiesSelectorModal'
import Entities from '@/components/pipelines/Entities'
import Extractors from '@/components/pipelines/Extractors'
import ExtractorSettingsModal from '@/components/pipelines/ExtractorSettingsModal'
import Loaders from '@/components/pipelines/Loaders'
import LoaderSettingsModal from '@/components/pipelines/LoaderSettingsModal'
import PipelineSchedules from '@/components/pipelines/PipelineSchedules'

import Dashboards from '@/views/Dashboards'
import Analyze from '@/views/Analyze'
import NotFound from '@/views/NotFound'
import Orchestration from '@/views/Orchestration'
import Pipelines from '@/views/Pipelines'
import Repo from '@/views/Repo'

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '*',
      name: '404',
      component: NotFound
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
            isModal: false
          }
        },
        {
          path: 'extractors/:extractor',
          name: 'extractorSettings',
          components: {
            default: Extractors,
            extractorSettings: ExtractorSettingsModal
          },
          meta: {
            isModal: true
          }
        },
        {
          path: 'entities',
          name: 'entities',
          components: {
            default: Entities
          },
          meta: {
            isModal: false
          }
        },
        {
          path: 'entities/:extractor',
          name: 'extractorEntities',
          components: {
            default: Entities,
            extractorEntities: EntitiesSelectorModal
          },
          meta: {
            isModal: true
          }
        },
        {
          path: 'loaders',
          name: 'loaders',
          components: {
            default: Loaders
          },
          meta: {
            isModal: false
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
            isModal: true
          }
        },
        {
          path: 'schedules',
          name: 'schedules',
          components: {
            default: PipelineSchedules
          },
          meta: {
            isModal: false
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
            isModal: true
          }
        }
      ]
    },
    {
      path: '/orchestration/',
      name: 'orchestration',
      component: Orchestration
    },
    {
      path: '/files/',
      name: 'projectFiles',
      component: Repo
    },
    {
      path: '/analyze/',
      redirect: '/analyze/models/',
      name: 'analyze',
      component: Analyze,
      children: [
        {
          path: 'models',
          name: 'analyzeModels',
          component: AnalyzeModels
        },
        {
          path: 'settings',
          name: 'analyzeSettings',
          component: AnalyzeSettings
        },
        {
          path: '/analyze/:model/:design',
          name: 'analyzeDesign',
          component: Design
        },
        {
          path: '/analyze/:model/:design/reports/report/:slug',
          name: 'Report',
          component: Design
        }
      ]
    },
    {
      path: '/dashboards/',
      name: 'Dashboards',
      component: Dashboards
    },
    {
      path: '/dashboards/dashboard/:slug',
      name: 'Dashboard',
      component: Dashboards
    }
  ]
})

export default router
