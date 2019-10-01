<script>
import AnalyzeModels from '@/components/model/AnalyzeModels'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Model',
  components: {
    AnalyzeModels,
    RouterViewLayout
  }
}
</script>

<template>
  <router-view-layout>
    <div class="container view-body is-fluid">
      <AnalyzeModels></AnalyzeModels>
    </div>
  </router-view-layout>
</template>

<style lang="scss" scoped></style>
