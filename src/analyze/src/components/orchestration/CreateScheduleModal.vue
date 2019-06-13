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
                      <option>skip</option>
                      <option>only</option>
                      <option>run</option>
                    </select>
                  </span>
                </p>
              </td>
              <td>
                <p class="control is-expanded">
                  <span class="select is-fullwidth">
                    <select v-model="pipeline.interval">
                      <option>@once</option>
                      <option>@hourly</option>
                      <option>@daily</option>
                      <option>@weekly</option>
                      <option>@monthly</option>
                      <option>@yearly</option>
                    </select>
                  </span>
                </p>
              </td>
              <td>
                <p class="control is-expanded">
                  <Dropdown label="None" is-right-aligned is-full-width>
                    <div class="dropdown-content" slot-scope="{ dropdownForceClose }">
                      <a
                        class="dropdown-item"
                        @click="dropdownForceClose();">
                        None
                      </a>
                      <hr class="dropdown-divider">
                      <div>
                        <div class="dropdown-item">
                          <span class='is-size-7'>mm/dd/yyyy</span>
                          <input
                            type="date"
                            id="catchup-start"
                            name="catchup-start"
                            :value="todaysDate"
                            required pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}"
                            min="2000-01-01"
                            :max="todaysDate">
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
      return true;
    },
    todaysDate() {
      return utils.getTodayYYYYMMDD();
    },
  },
  data() {
    return {
      pipeline: {
        name: '',
        extractor: '',
        loader: '',
        transform: '',
        interval: '',
        startDate: 'None',
      },
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
    },
    save() {
      console.log('save:', this.pipeline);
    },
  },
};
</script>

<style lang="scss">
</style>
