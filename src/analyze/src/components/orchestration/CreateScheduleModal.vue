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
                    type="text"
                    @focus="$event.target.select()"
                    v-model='pipeline.name'
                    placeholder="Name">
                </p>
              </th>
              <td>
                <p class="control is-expanded">
                  <span class="select is-fullwidth">
                    <select
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
                  <span class="select is-fullwidth">
                    <select
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
                  <span class="select is-fullwidth">
                    <select v-model="pipeline.transform">
                      <option
                        v-for="transform in transformOptions"
                        :key='transform'>{{transform}}</option>
                    </select>
                  </span>
                </p>
              </td>
              <td>
                <p class="control is-expanded">
                  <span class="select is-fullwidth">
                    <select v-model="pipeline.interval">
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
                    :label='pipeline.startDate'
                    is-right-aligned
                    is-full-width>
                    <div class="dropdown-content" slot-scope="{ dropdownForceClose }">
                      <a
                        class="dropdown-item"
                        @click="setCatchUpDateToNone(); dropdownForceClose();">
                        None
                      </a>
                      <hr class="dropdown-divider">
                      <div>
                        <div class="dropdown-item">
                          <input
                            type="date"
                            id="catchup-start"
                            name="catchup-start"
                            v-model='pipeline.startDate'
                            pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}"
                            :min='`${minYear}-01-01`'
                            :max='todaysDate'>
                          <button
                            class="button is-interactive-primary is-outlined is-small"
                            :disabled='!isStartDateSettable'
                            @click="dropdownForceClose();">
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

<script>
import { mapGetters, mapState } from 'vuex';
import _ from 'lodash';

import Dropdown from '@/components/generic/Dropdown';

import utils from '@/utils/utils';

export default {
  name: 'CreateScheduleModal',
  components: {
    Dropdown,
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
    isSaveable() {
      const hasOwns = [];
      _.forOwn(this.pipeline, val => hasOwns.push(val));
      return hasOwns.find(val => val === '') === undefined;
    },
    isStartDateSettable() {
      return this.isStartDateValid && this.isStartDateMinYearValid;
    },
    isStartDateValid() {
      return utils.getIsDateStringInFormatYYYYMMDD(this.pipeline.startDate);
    },
    isStartDateMinYearValid() {
      return parseInt(this.pipeline.startDate.substring(0, 4)) >= this.minYear;
    },
    todaysDate() {
      return utils.getTodayYYYYMMDD();
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
      minYear: '2000',
      pipeline: {
        name: '',
        extractor: '',
        loader: '',
        transform: '',
        interval: '',
        startDate: 'None',
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
        this.$router.push({ name: 'schedule' });
      }
    },
    prefillForm() {
      // TODO implement an intelligent prefill approach
      this.pipeline.name = `Default-${this.todaysDate}`;
      this.pipeline.extractor = this.installedPlugins.extractors[0].name;
      this.pipeline.loader = this.installedPlugins.loaders[0].name;
      this.pipeline.transform = this.transformOptions[0];
      this.pipeline.interval = this.intervalOptions[0];
    },
    save() {
      /**
       * TODO
       * 1. add blur hooks -> to check that no existing schedule matches all the same values -> exising name doesn't already exist
       *  */
      console.log('save:', this.pipeline);
    },
    setCatchUpDateToNone() {
      this.pipeline.startDate = 'None';
    },
  },
};
</script>

<style lang="scss">
</style>
