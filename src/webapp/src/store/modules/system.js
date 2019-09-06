import lodash from 'lodash'
import poller from '@/utils/poller'
import utils from '@/utils/utils'
import systemApi from '@/api/system'
import compareVersions from 'compare-versions'

const defaultState = utils.deepFreeze({
  version: null,
  latestVersion: null
})

const getters = {
  updateAvailable(state) {
    if (state.latestVersion === null || state.version === null) {
      return false
    }

    return compareVersions.compare(state.latestVersion, state.version, '>')
  }
}

const actions = {
  upgrade({ state, commit }) {
    let upgradePoller = null

    const uponUpgrade = new Promise((resolve, reject) => {
      upgradePoller = poller.create(
        () => {
          systemApi
            .version()
            .then(response => {
              const { latestVersion, version } = response.data
              if (compareVersions.compare(state.version, latestVersion, '=')) {
                commit('setLatestVersion', latestVersion)
                reject(version)
              }

              if (compareVersions.compare(version, state.version, '>')) {
                commit('setVersion', version)

                // refresh the page?
                resolve(version)
              }
            })
            .catch(() => {
              // the host might be down for a while during the update process.
              console.info('Waiting for API to restart...')
            })
        },
        null,
        5000
      )

      // register the poller and trigger the upgrade
      systemApi
        .upgrade()
        .then(() => commit('setUpdating', true))
        .then(upgradePoller.init)
    })

    return uponUpgrade.finally(() => {
      // cleanup
      upgradePoller.dispose()
      commit('setUpdating', false)
    })
  },
  check({ commit }) {
    return systemApi.version().then(response => {
      commit('setVersion', response.data.version)
      commit('setLatestVersion', response.data.latestVersion)
    })
  }
}

const mutations = {
  setVersion(state, version) {
    state.version = version
  },

  setLatestVersion(state, version) {
    state.latestVersion = version
  },

  setUpdating(state, updating) {
    state.updating = updating
  }
}

export default {
  namespaced: true,
  state: lodash.cloneDeep(defaultState),
  getters,
  actions,
  mutations
}
