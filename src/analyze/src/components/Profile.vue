<template>
  <span>
    @{{identity.username}}
  </span>
</template>

<script>
import jwtDecode from 'jwt-decode';

export default {
  data() {
    const jwt = jwtDecode(this.$auth.authToken);

    return {
      identity: jwt.identity,
    };
  },
}
</script>
