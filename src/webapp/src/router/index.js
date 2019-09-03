import Router from 'vue-router'

import AnalyzeModels from '@/components/analyze/AnalyzeModels'
import AnalyzeSettings from '@/components/analyze/AnalyzeSettings'
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
          path: 'extractors/:extractor/configure',
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
          path: 'extractors/:extractor/select',
          name: 'extractorEntities',
          components: {
            default: Extractors,
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
          path: 'transforms',
          name: 'transforms',
          components: {
            default: Transforms
          },
          meta: {
            isModal: false
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
          name: 'report',
          component: Design
        }
      ]
    },
    {
      path: '/dashboards/',
      name: 'dashboards',
      component: Dashboards
    },
    {
      path: '/dashboards/dashboard/:slug',
      name: 'dashboard',
      component: Dashboards
    }
  ]
})

export default router
