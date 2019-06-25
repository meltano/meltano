<script>
import { mapGetters, mapState } from 'vuex';

import Dropdown from '@/components/generic/Dropdown';
import InputDateIso8601 from '@/components/generic/InputDateIso8601';

import utils from '@/utils/utils';

import _ from 'lodash';

export default {
  name: 'CreateScheduleModal',
  components: {
    Dropdown,
    InputDateIso8601,
  },
  created() {
    this.$store.dispatch('plugins/getInstalledPlugins')
      .then(this.prefillForm);
  },
  computed: {
    ...mapGetters('plugins', [
      'getHasInstalledPluginsOfType',
    ]),
    ...mapState('plugins', [
      'installedPlugins',
    ]),
    getFormattedDateStringYYYYMMDD() {
      return utils.formatDateStringYYYYMMDD(this.pipeline.startDate);
    },
    getInputDateMeta() {
      return utils.getInputDateMeta();
    },
    isSaveable() {
      const hasOwns = [];
      _.forOwn(this.pipeline, val => hasOwns.push(val));
      return hasOwns.find(val => val === '') === undefined;
    },
  },
  data() {
    return {
      intervalOptions: [
        '@once',
        '@hourly',
        '@daily',
        '@weekly',
        '@monthly',
        '@yearly',
      ],
      hasCatchupDate: false,
      pipeline: {
        name: '',
        extractor: '',
        loader: '',
        transform: '',
        interval: '',
        startDate: null,
      },
      transformOptions: [
        'skip',
        'run',
        'only',
      ],
    };
  },
  methods: {
    close() {
      if (this.prevRoute) {
        this.$router.go(-1);
      } else {
        this.$router.push({ name: 'schedules' });
      }
    },
    prefillForm() {
      // TODO implement an intelligent prefill approach
      this.pipeline.name = `Default-${this.getInputDateMeta.today}`;
      this.pipeline.extractor = !_.isEmpty(this.installedPlugins.extractors)
        ? this.installedPlugins.extractors[0].name : '';
      this.pipeline.loader = !_.isEmpty(this.installedPlugins.loaders)
        ? this.installedPlugins.loaders[0].name : '';
      this.pipeline.transform = !_.isEmpty(this.transformOptions)
        ? this.transformOptions[0] : '';
      this.pipeline.interval = !_.isEmpty(this.intervalOptions)
        ? this.intervalOptions[0] : '';
    },
    save() {
      this.$store.dispatch('configuration/savePipelineSchedule', this.pipeline)
        .then(() => this.close());
    },
    setHasCatchupDate(val) {
      this.hasCatchupDate = val;
      if (!this.hasCatchupDate) {
        this.pipeline.startDate = null;
      }
    },
  },
};
</script>

<template>

  <div class="modal is-active">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card is-wide">
      <header class="modal-card-head">
        <p class="modal-card-title">Create Pipeline Schedule</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body">

        <table class="table pipelines-table is-fullwidth">
          <thead>
            <tr>
              <th>Name</th>
              <th class='has-text-centered'>Extractor</th>
              <th class='has-text-centered'>Loader</th>
              <th class='has-text-centered'>Transform</th>
              <th class='has-text-centered'>Interval</th>
              <th class='has-text-centered'>Catch-up Date</th>
            </tr>
          </thead>

          <tbody>
            <tr>
              <th>
                <p class="control is-expanded">
                  <input
                    class="input"
                    :class="{
                      'is-interactive-secondary has-text-interactive-secondary': pipeline.name }"
                    type="text"
                    @focus="$event.target.select()"
                    v-model='pipeline.name'
                    placeholder="Name">
                </p>
              </th>
              <td>
                <p class="control is-expanded">
                  <span
                    class="select is-fullwidth"
                    :class="{
                      'is-interactive-secondary': pipeline.extractor,
                      'is-loading': !pipeline.extractor }">
                    <select
                      :class="{ 'has-text-interactive-secondary': pipeline.extractor }"
                      v-model="pipeline.extractor"
                      :disabled='!getHasInstalledPluginsOfType("extractors")'>
                      <option
                        v-for="extractor in installedPlugins.extractors"
                        :key='extractor.name'>{{extractor.name}}</option>
                    </select>
                  </span>
                </p>
              </td>
              <td>
                <p class="control is-expanded">
                  <span
                    class="select is-fullwidth"
                    :class="{
                      'is-interactive-secondary': pipeline.loader,
                      'is-loading': !pipeline.loader }">
                    <select
                      :class="{ 'has-text-interactive-secondary': pipeline.loader }"
                      v-model="pipeline.loader"
                      :disabled='!getHasInstalledPluginsOfType("loaders")'>
                      <option
                        v-for="loader in installedPlugins.loaders"
                        :key='loader.name'>{{loader.name}}</option>
                    </select>
                  </span>
                </p>
              </td>
              <td>
                <p class="control">
                  <span
                    class="select is-fullwidth"
                    :class="{
                      'is-interactive-secondary': pipeline.transform,
                      'is-loading': !pipeline.transform }">
                    <select
                      :class="{ 'has-text-interactive-secondary': pipeline.transform }"
                      v-model="pipeline.transform">
                      <option
                        v-for="transform in transformOptions"
                        :key='transform'>{{transform}}</option>
                    </select>
                  </span>
                </p>
              </td>
              <td>
                <p class="control is-expanded">
                  <span
                    class="select is-fullwidth"
                    :class="{
                      'is-interactive-secondary': pipeline.interval,
                      'is-loading': !pipeline.interval }">
                    <select
                      :class="{ 'has-text-interactive-secondary': pipeline.interval }"
                      v-model="pipeline.interval">
                      <option
                        v-for="interval in intervalOptions"
                        :key='interval'>{{interval}}</option>
                    </select>
                  </span>
                </p>
              </td>
              <td>
                <p class="control is-expanded">
                  <Dropdown
                    :label='hasCatchupDate ? getFormattedDateStringYYYYMMDD : "None"'
                    :button-classes='(pipeline.startDate || !hasCatchupDate)
                      ? "is-interactive-secondary is-outlined" : ""'
                    is-right-aligned
                    is-full-width>
                    <div class="dropdown-content" slot-scope="{ dropdownForceClose }">
                      <a
                        class="dropdown-item"
                        @click="setHasCatchupDate(false); dropdownForceClose();">
                        None
                      </a>
                      <hr class="dropdown-divider">
                      <div>
                        <div class="dropdown-item">
                          <InputDateIso8601
                            v-model="pipeline.startDate"
                            name='catchup-start' />
                          <button
                            class="button is-interactive-primary is-outlined is-small"
                            @click="setHasCatchupDate(true); dropdownForceClose();">
                            Set
                          </button>
                        </div>
                      </div>
                    </div>
                  </Dropdown>
                </p>
              </td>
            </tr>
          </tbody>
        </table>

      </section>
      <footer class="modal-card-foot buttons is-right">
        <button
          class="button"
          @click="close">Cancel</button>
        <button
          class='button is-interactive-primary'
          :disabled="!isSaveable"
          @click='save'>Save</button>
      </footer>
    </div>
  </div>

</template>

<style lang="scss">
</style>
