<template>
  <div>

    <div class="columns">
      <div class="column is-three-fifths is-offset-one-fifth">
        <div class='content has-text-centered'>
          <p class='level-item buttons'>
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Create a data pipeline below</span>
            </a>
            <span class='step-spacer'>then</span>
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Click <span class='is-italic'>Run</span> to schedule it</span>
            </a>
          </p>
        </div>
      </div>
    </div>

    <br>

    <div class="columns is-vcentered">

      <div class="column">
        <h2 class='title is-5'>Existing</h2>
      </div>

      <div class="column">
        <div class="field is-pulled-right">

          <p class="control">
            <button
              class="button is-interactive-primary"
              @click="createPipeline();">
              <span>Create</span>
            </button>
          </p>

        </div>
      </div>

    </div>

    <div class="box">

      <table class="table pipelines-table is-fullwidth">
        <thead>
          <tr>
            <th>Name</th>
            <th class='has-text-centered'>Extractor</th>
            <th class='has-text-centered'>Loader</th>
            <th class='has-text-centered'>Transform</th>
            <th class='has-text-centered'>Interval</th>
            <th class='has-text-centered'>Start Date</th>
            <th class='has-text-centered'></th>
          </tr>
        </thead>
        <tbody>

          <template v-for="pipeline in [{id: 1}, {id: 2}]">
            <tr :key='pipeline.id'>
              <th>
                <p class="control is-expanded">
                  <input class="input" type="text" placeholder="Name">
                </p>
              </th>
              <td>
                <p class="control is-expanded">
                  <span class="select is-fullwidth">
                    <select>
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
                    <select>
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
                    <select>
                      <option>Skip</option>
                      <option>Only</option>
                      <option>Run</option>
                    </select>
                  </span>
                </p>
              </td>
              <td>
                <p class="control is-expanded">
                  <span class="select is-fullwidth">
                    <select>
                      <option>None</option>
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
                            :id="`catchup-start-${pipeline.id}`"
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
              <td>
                <p class="control">
                  <button disabled class="button is-interactive-primary is-fullwidth">
                    Save
                  </button>
                </p>
              </td>
            </tr>
          </template>

        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
import { mapState } from 'vuex';

import Dropdown from '@/components/generic/Dropdown';

import utils from '@/utils/utils';

export default {
  name: 'PipelineSchedules',
  components: {
    Dropdown,
  },
  created() {
    this.$store.dispatch('plugins/getInstalledPlugins');
  },
  computed: {
    ...mapState('configuration', [
      'pipelines',
    ]),
    ...mapState('plugins', [
      'installedPlugins',
    ]),
    todaysDate() {
      return utils.getTodayYYYYMMDD();
    },
  },
  methods: {
    createPipeline() {
      this.$router.push({ name: 'createSchedule' });
    },
  },
};
</script>

<style lang="scss">
</style>
