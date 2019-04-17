<template>
  <div class="proxy-container">
    <p class="disclaimer">You are now looking at the Airflow UI.</p>
    <iframe class="proxy" src="http://localhost:9000/" />
  </div>
</template>
<script>
</script>
<style>
 .proxy-container {
   display: flex;
   flex-grow: 1;
   flex-direction: column;
 }

 .disclaimer {
   font-size: 0.8rem;
   padding: 0.3rem;
   color: white;
   text-align: center;
   background: #5555aa;
 }

 .proxy {
   flex: 1;
 }
</style>
