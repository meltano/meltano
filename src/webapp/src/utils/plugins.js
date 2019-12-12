export default {
  filterVisiblePlugins(state, pluginType) {
    const plugins = state.plugins[pluginType] || []

    return plugins.filter(plugin => {
      const installedPlugins = state.installedPlugins[pluginType] || []

      if (
        installedPlugins.find(
          installedPlugin => installedPlugin.name === plugin.name
        )
      ) {
        return true
      } else {
        return !plugin.hidden
      }
    })
  }
}
