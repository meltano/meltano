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

    <div class="columns">

      <div class="column">

        <div>

          <div class="field has-addons">
            <p class="control is-expanded">
              <input class="input" type="text" placeholder="Name">
            </p>
            <p class="control">
              <span class="select">
                <select>
                  <option value="" disabled selected hidden>Extractor</option>
                  <option>Aaaaa</option>
                  <option>Bbbbb</option>
                  <option>Ccccc</option>
                </select>
              </span>
            </p>
            <p class="control">
              <span class="select">
                <select>
                  <option value="" disabled selected hidden>Loader</option>
                  <option>Aaaaa</option>
                  <option>Bbbbb</option>
                  <option>Ccccc</option>
                </select>
              </span>
            </p>
            <p class="control">
              <Dropdown label="Catchup Date" is-right-aligned>
                <div class="dropdown-content" slot-scope="{ dropdownForceClose }">
                  <a
                    class="dropdown-item"
                    @click="dropdownForceClose();">
                    None
                  </a>
                  <hr class="dropdown-divider">
                  <div>
                    <div class="dropdown-item">
                      Data picker UI here...
                    </div>
                  </div>
                </div>
              </Dropdown>
            </p>
            <p class="control">
              <span class="select">
                <select>
                  <option value="" disabled selected hidden>Run Frequency</option>
                  <option>Aaaaa</option>
                  <option>Bbbbb</option>
                  <option>Ccccc</option>
                </select>
              </span>
            </p>
            <p class="control">
              <button disabled class="button is-interactive-primary">
                Run
              </button>
            </p>
          </div>

        </div>

      </div>
    </div>

  </div>
</template>

<script>
import Dropdown from '@/components/generic/Dropdown';

export default {
  name: 'PipelineSchedules',
  components: {
    Dropdown
  }
};
</script>

<style lang="scss">
</style>
