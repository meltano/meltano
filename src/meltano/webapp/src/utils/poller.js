function JobPoller(pollFn, pollFnMetadata, delay) {
  let poller

  function getMetadata() {
    return pollFnMetadata
  }

  function poll() {
    pollFn(pollFnMetadata)
  }

  function dispose() {
    clearInterval(poller)
  }

  function init() {
    poller = setInterval(poll, delay)
  }

  return {
    init,
    getMetadata,
    dispose,
  }
}

export default {
  create(pollFn, pollFnMetadata, delay) {
    return new JobPoller(pollFn, pollFnMetadata, delay)
  },
}
