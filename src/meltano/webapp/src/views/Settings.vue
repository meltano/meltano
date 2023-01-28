<script>
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Settings',
  components: {
    RouterViewLayout,
  },
  data() {
    return {
      categories: [
        {
          name: 'Database',
          pages: [
            {
              title: 'Database',
              href: '/settings/database',
            },
          ],
        },
        {
          name: 'Access control',
          pages: [
            {
              title: 'Roles',
              href: '/settings/roles',
            },
          ],
        },
        {
          name: 'Connectors',
          pages: [
            {
              title: 'Extractors',
              href: '/settings/connectors#extractors',
            },
            {
              title: 'Loaders',
              href: '/settings/connectors#loaders',
            },
          ],
        },
      ],
    }
  },
}
</script>

<template>
  <router-view-layout>
    <div class="container view-body is-widescreen">
      <section>
        <div class="columns is-gapless">
          <div class="column is-one-quarter">
            <ul class="menu-list">
              <router-link tag="li" :to="{ name: 'database' }">
                <a>Database</a>
              </router-link>
              <router-link tag="li" :to="{ name: 'connectors' }">
                <a>Connectors</a>
              </router-link>
            </ul>
          </div>

          <div class="column is-three-quarters">
            <router-view />
          </div>
        </div>
      </section>
    </div>
  </router-view-layout>
</template>

<style lang="scss"></style>
