<script>
import BaseCard from '@/components/generic/BaseCard'

export default {
  name: 'ConnectorCard',
  components: {
    BaseCard
  },
  props: {
    connector: {
      required: true
    }
  },
  computed: {
    connectorName() {
      if (this.connector.indexOf('tap') > -1) {
        return this.connector.replace('tap-', '');
      } else {
        return this.connector.replace('target-', '');
      }
    }
  }
}
</script>

<template>
	<BaseCard>
    <div class="cc-wrapper">
      <div class="cc-logo">
        <img :src="`/static/logos/${connectorName}-logo.png`" 
          :alt="`${connectorName} logo`" 
          class="cc-image" 
        />
      </div>
      <div style="padding-top: 0;">
        <h3 style="margin-top: 0; margin-bottom: 10px;">{{ connector }}</h3>
        <p style="font-size: 1rem;">This data source focuses on getting emissions data from local areas.</p>
        <p><a href="#">More information about {{ connectorName }} tap</a></p>
      </div>
    </div>
    <div>
      <slot name="callToAction"></slot>
    </div>
  </BaseCard>
</template>

<style lang="scss">
.cc-logo {
  display: flex; 
  align-items: center; 
  margin-bottom: 0; 
  justify-content: center; 
  margin-top: 15px; 
  margin-bottom: 10px; 
  min-width: 150px; 
  padding: 30px; 
  box-sizing: border-box;
}

.cc-wrapper {
  display: flex; 
  margin: 20px 0; 
  align-items: center; 
  flex: 1;
}

.cc-image {
  max-width: 150px; 
  padding: 15px;
}
</style>
