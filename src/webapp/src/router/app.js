import Router from 'vue-router'

import CreatePipelineScheduleModal from '@/components/pipelines/CreatePipelineScheduleModal'
import LogModal from '@/components/pipelines/LogModal'
import PluginSettingsModal from '@/components/pipelines/PluginSettingsModal'
import CronJobModal from '@/components/pipelines/CronJobModal'

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
        title: 'Meltano: Not Found',
      },
    },
    {
      path: '/',
      redirect: '/extractors',
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
            extractorSettings: PluginSettingsModal,
          },
          props: { extractorSettings: { pluginType: 'extractors' } },
          meta: {
            isModal: true,
            title: 'Meltano: Data Extractor Configuration',
          },
        },
      ],
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
            loaderSettings: PluginSettingsModal,
          },
          props: { loaderSettings: { pluginType: 'loaders' } },
          meta: {
            isModal: true,
            title: 'Meltano: Data Loader Configuration',
          },
        },
      ],
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
            createPipelineSchedule: CreatePipelineScheduleModal,
          },
          meta: {
            isModal: true,
            title: 'Meltano: Create pipelines',
          },
        },
        {
          path: ':stateId',
          name: 'runLog',
          components: {
            default: Pipelines,
            runLog: LogModal,
          },
          meta: {
            isModal: true,
            title: 'Meltano: Job Log',
          },
        },
        {
          path: '/cron-job-settings/:stateId',
          name: 'cronJobSettings',
          components: {
            default: Pipelines,
            cronJobSettings: CronJobModal,
          },
          meta: {
            isModal: true,
            title: 'Meltano: Cron Job Settings',
          },
        },
      ],
    },
  ],
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'Meltano'
  next()
})

export default router
