export default {
  filterAvailablePlugins({ installedPlugins = [], pluginList = [] }) {
    return pluginList.filter((plugin) => {
      const isPluginInstalled = Boolean(
        installedPlugins.find(
          (installedPlugin) => installedPlugin.name === plugin.name
        )
      )
      return !isPluginInstalled && !plugin.hidden
    })
  },
}
