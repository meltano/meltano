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
            <th class='has-text-centered'>Run</th>
          </tr>
        </thead>
        <tbody>
          <tr>
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
                      v-for="extractor in plugins.extractors"
                      :key='extractor'>{{extractor}}</option>
                  </select>
                </span>
              </p>
            </td>
            <td>
              <p class="control is-expanded">
                <span class="select is-fullwidth">
                  <select>
                    <option value="" disabled selected hidden>Loader</option>
                    <option>Aaaaa</option>
                    <option>Bbbbb</option>
                    <option>Ccccc</option>
                  </select>
                </span>
              </p>
            </td>
            <td>
              <p class="control">
                <label class="checkbox">
                  <input type="checkbox">
                  Transforms
                </label>
              </p>
            </td>
            <td>
              <p class="control is-expanded">
                <span class="select is-fullwidth">
                  <select>
                    <option value="" disabled selected hidden>Interval</option>
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
                <Dropdown label="Start Date" is-right-aligned is-full-width>
                  <div class="dropdown-content" slot-scope="{ dropdownForceClose }">
                    <a
                      class="dropdown-item"
                      @click="dropdownForceClose();">
                      None
                    </a>
                    <hr class="dropdown-divider">
                    <div>
                      <div class="dropdown-item">
                        Date picker UI here...
                      </div>
                    </div>
                  </div>
                </Dropdown>
              </p>
            </td>
            <td>
              <p class="control">
                <button disabled class="button is-interactive-primary is-fullwidth">
                  Run
                </button>
              </p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
import { mapState } from 'vuex';

import Dropdown from '@/components/generic/Dropdown';

export default {
  name: 'PipelineSchedules',
  components: {
    Dropdown,
  },
  created() {
    this.$store.dispatch('plugins/getInstalledPlugins');
  },
  computed: {
    ...mapState('plugins', [
      'plugins',
    ]),
  },
};
</script>

<style lang="scss">
</style>
