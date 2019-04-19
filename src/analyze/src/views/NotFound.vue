<script>
export default {
  name: 'NotFound',
};
</script>

<template>
  <main :class="$style.wrapper">
    <div :class="$style.content">
      <h1 :class="$style.h1">404</h1>
      <p :class="$style.text">Oops... Seems this page is missing...</p>
      <ul :class="$style.list">
        <li><a href="/" :class="$style.button">Go back home</a></li>
      </ul>
    </div>
  </main>
</template>

<style lang="scss" module>
@import "../scss/bulma-preset-overrides.scss";

.wrapper {
  height: calc(100vh - #{$navbar-height});
  display: flex;
  justify-content: center;
}

.content {
  text-align: center;
}

.h1 {
  font-size: 5rem;
  font-weight: bold;
  margin-top: 3rem;
}

.text {
  font-size: 1.5rem;
}

.list {
  margin-top: 3rem;
}

.button {
  padding: 20px;
  background-color: rgb(36, 102, 167);
  color: #fff;
  border-radius: 8px;
  transition: background 0.2s ease-in;

  &:hover {
    color: #fff;
    background-color: #0F3B66;
  }
}
</style>
