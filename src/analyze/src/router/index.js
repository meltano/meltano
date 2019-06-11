import Router from 'vue-router';

import AnalyzeModels from '@/components/designs/AnalyzeModels';
import AnalyzeSettings from '@/components/designs/AnalyzeSettings';
import EntitiesSelectorModal from '@/components/orchestration/EntitiesSelectorModal';
import Entities from '@/components/orchestration/Entities';
import Extractors from '@/components/orchestration/Extractors';
import ExtractorSettingsModal from '@/components/orchestration/ExtractorSettingsModal';
import Loaders from '@/components/orchestration/Loaders';
import LoaderSettingsModal from '@/components/orchestration/LoaderSettingsModal';
import PipelineSchedules from '@/components/orchestration/PipelineSchedules';

import Dashboards from '@/views/Dashboards';
import Design from '@/views/Design';
import Designs from '@/views/Designs';
import NotFound from '@/views/NotFound';
import Orchestration from '@/views/Orchestration';
import Pipelines from '@/views/Pipelines';
import Repo from '@/views/Repo';

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '*',
      name: '404',
      component: NotFound,
    },
    {
      path: '/',
      redirect: '/pipelines',
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
            default: Extractors,
          },
          meta: {
            isModal: false,
          },
        },
        {
          path: 'extractors/:extractor',
          name: 'extractorSettings',
          components: {
            default: Extractors,
            extractorSettings: ExtractorSettingsModal,
          },
          meta: {
            isModal: true,
          },
        },
        {
          path: 'entities',
          name: 'entities',
          components: {
            default: Entities,
          },
          meta: {
            isModal: false,
          },
        },
        {
          path: 'entities/:extractor',
          name: 'extractorEntities',
          components: {
            default: Entities,
            extractorEntities: EntitiesSelectorModal,
          },
          meta: {
            isModal: true,
          },
        },
        {
          path: 'loaders',
          name: 'loaders',
          components: {
            default: Loaders,
          },
          meta: {
            isModal: false,
          },
        },
        {
          path: 'loaders/:loader',
          name: 'loaderSettings',
          components: {
            default: Loaders,
            loaderSettings: LoaderSettingsModal,
          },
          meta: {
            isModal: true,
          },
        },
        {
          path: 'schedule',
          name: 'schedule',
          component: PipelineSchedules,
        },
      ],
    },
    {
      path: '/orchestration/',
      name: 'orchestration',
      component: Orchestration,
    },
    {
      path: '/files/',
      name: 'projectFiles',
      component: Repo,
    },
    {
      path: '/analyze/',
      redirect: '/analyze/models/',
      name: 'analyze',
      component: Designs,
      children: [
        {
          path: 'models',
          name: 'analyzeModels',
          component: AnalyzeModels,
        },
        {
          path: 'connection-settings',
          name: 'analyzeSettings',
          component: AnalyzeSettings,
        },
      ],
    },
    {
      path: '/analyze/:model/:design',
      name: 'analyze_design',
      component: Design,
    },
    {
      path: '/analyze/:model/:design/reports/report/:slug',
      name: 'Report',
      component: Design,
    },
    {
      path: '/dashboards/',
      name: 'Dashboards',
      component: Dashboards,
    },
    {
      path: '/dashboards/dashboard/:slug',
      name: 'Dashboard',
      component: Dashboards,
    },
  ],
});

export default router;
