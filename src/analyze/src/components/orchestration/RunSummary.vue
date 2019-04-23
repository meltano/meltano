<template>
  <div>

    <div class="columns">

      <div class="column box is-4 is-offset-4">
        <article class="message is-warning is-small">
          <div class="message-header">
            <p>Take Note</p>
          </div>
          <div class="message-body">
            <div class="content">
                          <p>A summary of your ELT related settings will go here in the future. <a target="_blank" href="https://gitlab.com/meltano/meltano/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=&issuable_template=feature_proposal">Get in touch if you have opinions about what should live here</a>.</p>

            </div>
            <div class="content">
              <p>For example:</p>
              <ul>
                <li>Does it make sense to have Transformations and Orchestration here?</li>
                <li>Why or why not?</li>
                <li>What would be helpful to see (if anything) for an ELT summary?</li>
              </ul>
            </div>
          </div>
        </article>

        <div class="buttons is-pulled-right">
          <button
            disabled
            class='button is-success'>Run ELT</button>
        </div>

      </div>
    </div>

  </div>
</template>

<script>

export default {
  name: 'RunSummary',
};
</script>

<style lang="scss">
</style>
