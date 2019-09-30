import compareVersions from 'compare-versions'
import lodash from 'lodash'

import poller from '@/utils/poller'
import systemApi from '@/api/system'
import utils from '@/utils/utils'

const defaultState = utils.deepFreeze({
  latestVersion: null,
  updating: false,
  version: null
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
  check({ commit }) {
    return systemApi.version({ include_latest: true }).then(response => {
      commit('setVersion', response.data.version)
      commit('setLatestVersion', response.data.latestVersion)
    })
  },
  upgrade({ state, commit }) {
    let upgradePoller = null

    const uponUpgrade = new Promise((resolve, reject) => {
      upgradePoller = poller.create(
        () => {
          systemApi
            .version()
            .then(response => {
              const { version } = response.data
              if (compareVersions.compare(version, state.latestVersion, '>=')) {
                commit('setVersion', version)
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
  }
}

const mutations = {
  setLatestVersion(state, version) {
    state.latestVersion = version
  },

  setUpdating(state, updating) {
    state.updating = updating
  },

  setVersion(state, version) {
    state.version = version
  }
}

export default {
  namespaced: true,
  state: lodash.cloneDeep(defaultState),
  getters,
  actions,
  mutations
}
