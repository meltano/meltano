<script>
import { mapActions, mapGetters, mapState } from 'vuex';
import capitalize from '@/filters/capitalize';
import underscoreToSpace from '@/filters/underscoreToSpace';

export default {
  created() {
    this.$store.dispatch('plugins/getAllPlugins');
    this.$store.dispatch('plugins/getInstalledPlugins');
    this.$store.dispatch('repos/getModels');
  },
  computed: {
    ...mapState('plugins', [
      'installedPlugins',
      'plugins',
    ]),
    ...mapGetters('repos', [
      'hasModels',
      'urlForModelDesign',
    ]),
    ...mapGetters('plugins', [
      'getIsPluginInstalled',
      'getIsInstallingPlugin',
    ]),
    ...mapState('repos', [
      'models',
    ]),
  },
  filters: {
    capitalize,
    underscoreToSpace,
  },
  methods: {
    ...mapActions('plugins', [
      'addPlugin',
      'installPlugin',
    ]),
    installModel(model) {
      this.addPlugin({ pluginType: 'models', name: model })
        .then(() => this.installPlugin({ pluginType: 'models', name: model }))
        .then(() => this.$store.dispatch('repos/getModels'));
    },
  },
};
</script>

<template>
  <section>
    <div class="columns">
      <div class="column is-one-third">
        <h2 class='title is-5'>Available</h2>

        <table class="table is-fullwidth is-narrow is-hoverable is-size-7 has-background-transparent ">
          <thead>
            <tr>
              <th>Action</th>
              <th>Model</th>
            </tr>
          </thead>
          <tbody>

            <template v-for='(modelPlugin, index) in plugins.models'>
              <tr :key="`${modelPlugin}-${index}`">
                <td>
                  <div class="buttons">
                    <a
                      v-if='!getIsPluginInstalled("models", modelPlugin)'
                      :class='{ "is-loading": getIsInstallingPlugin("models", modelPlugin) }'
                      class='button is-interactive-primary is-outlined is-block is-small'
                      @click="installModel(modelPlugin)">Install</a>
                    <a
                      v-else
                      disabled
                      class='button is-outlined is-block is-small tooltip is-tooltip-right'
                      data-tooltip="Not implemented">Uninstall</a>
                  </div>
                </td>
                <td>
                  <p>{{modelPlugin}}</p>
                </td>

              </tr>

            </template>

          </tbody>
        </table>

        <!-- <div class="content is-small">
          <div
            class="columns columns-compact-list"
            v-for='(modelPlugin, index) in plugins.models'
            :key="`${modelPlugin}-${index}`">
            <div class='column is-one-third'>
              <a
                v-if='!getIsPluginInstalled("models", modelPlugin)'
                :class='{ "is-loading": getIsInstallingPlugin("models", modelPlugin) }'
                class='button is-interactive-primary is-outlined is-block is-small'
                @click="installModel(modelPlugin)">Install</a>
              <a
                v-else
                disabled
                class='button is-outlined is-block is-small tooltip is-tooltip-left'
                data-tooltip="Not implemented">Uninstall</a>
            </div>
            <div class="column is-three-thirds">
              {{modelPlugin}}
            </div>
          </div>

        </div> -->
      </div>
      <div class="column is-two-thirds">
        <h2 class='title is-5'>Installed</h2>
        <template v-if='hasModels'>
          <div
            class="box"
            v-for="(v, model) in models" :key="`${model}-panel`">
            <div class="content">
              <h3 class='is-size-6'>{{model | capitalize | underscoreToSpace}}</h3>
              <hr class='hr-tight'>
              <div class="level level-tight" v-for="design in v['designs']" :key="design">
                <div class='level-left'>{{design | capitalize | underscoreToSpace}}</div>
                <div class="level-right">
                  <router-link
                    class="button is-small is-interactive-primary"
                    :to='urlForModelDesign(model, design)'>Analyze</router-link>
                </div>
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="content">
            <p>There are no models installed yet: you may install them using the panel on the left.</p>
          </div>
        </template>
      </div>
    </div>
  </section>
</template>

<style lang="scss">
</style>
