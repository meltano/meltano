<script>
import { mapGetters, mapState } from 'vuex';

import Dropdown from '@/components/generic/Dropdown';
import InputDateIso8601 from '@/components/generic/InputDateIso8601';
import ScheduleTableHead from '@/components/pipelines/ScheduleTableHead';

import utils from '@/utils/utils';

import _ from 'lodash';

export default {
  name: 'CreateScheduleModal',
  components: {
    Dropdown,
    InputDateIso8601,
    ScheduleTableHead,
  },
  created() {
    this.$store.dispatch('plugins/getInstalledPlugins')
      .then(this.prefillForm);
  },
  mounted() {
    this.$refs.name.focus();
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
      this.pipeline.name = '';
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

        <table class="table is-fullwidth">

          <ScheduleTableHead />

          <tbody>
            <tr>
              <td>
                <div class="control is-expanded">
                  <input
                    class="input"
                    :class="{
                      'is-success has-text-success': pipeline.name }"
                    type="text"
                    ref='name'
                    @focus="$event.target.select()"
                    v-model='pipeline.name'
                    placeholder="Name">
                </div>
              </td>
              <td>
                <div class="control is-expanded">
                  <span
                    class="select is-fullwidth"
                    :class="{
                      'is-success': pipeline.extractor,
                      'is-loading': !pipeline.extractor }">
                    <select
                      :class="{ 'has-text-success': pipeline.extractor }"
                      v-model="pipeline.extractor"
                      :disabled='!getHasInstalledPluginsOfType("extractors")'>
                      <option
                        v-for="extractor in installedPlugins.extractors"
                        :key='extractor.name'>{{extractor.name}}</option>
                    </select>
                  </span>
                </div>
              </td>
              <td>
                <div class="control is-expanded">
                  <span
                    class="select is-fullwidth"
                    :class="{
                      'is-success': pipeline.loader,
                      'is-loading': !pipeline.loader }">
                    <select
                      :class="{ 'has-text-success': pipeline.loader }"
                      v-model="pipeline.loader"
                      :disabled='!getHasInstalledPluginsOfType("loaders")'>
                      <option
                        v-for="loader in installedPlugins.loaders"
                        :key='loader.name'>{{loader.name}}</option>
                    </select>
                  </span>
                </div>
              </td>
              <td>
                <div class="control">
                  <span
                    class="select is-fullwidth"
                    :class="{
                      'is-success': pipeline.transform,
                      'is-loading': !pipeline.transform }">
                    <select
                      :class="{ 'has-text-success': pipeline.transform }"
                      v-model="pipeline.transform">
                      <option
                        v-for="transform in transformOptions"
                        :key='transform'>{{transform}}</option>
                    </select>
                  </span>
                </div>
              </td>
              <td>
                <div class="control is-expanded">
                  <span
                    class="select is-fullwidth"
                    :class="{
                      'is-success': pipeline.interval,
                      'is-loading': !pipeline.interval }">
                    <select
                      :class="{ 'has-text-success': pipeline.interval }"
                      v-model="pipeline.interval">
                      <option
                        v-for="interval in intervalOptions"
                        :key='interval'>{{interval}}</option>
                    </select>
                  </span>
                </div>
              </td>
              <td>
                <div class="control is-expanded">
                  <Dropdown
                    :label='hasCatchupDate ? getFormattedDateStringYYYYMMDD : "None"'
                    :button-classes='(pipeline.startDate || !hasCatchupDate)
                      ? "is-success is-outlined" : ""'
                    is-right-aligned
                    is-full-width>
                    <div class="dropdown-content" slot-scope="{ dropdownClose }">
                      <a
                        class="dropdown-item"
                        @click="setHasCatchupDate(false); dropdownClose();">
                        None
                      </a>
                      <hr class="dropdown-divider">
                      <div>
                        <div class="dropdown-item">
                          <InputDateIso8601
                            v-model="pipeline.startDate"
                            name='catchup-start'
                            input-classes='is-small' />
                          <button
                            class="button is-interactive-primary is-outlined is-small is-inline"
                            @click="setHasCatchupDate(true); dropdownClose();">
                            Set
                          </button>
                        </div>
                      </div>
                    </div>
                  </Dropdown>
                </div>
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
