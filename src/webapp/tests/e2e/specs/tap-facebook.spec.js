function waitForPoll(route, condition, options) {
  // Add limit on tries/time?
  cy.wait(route, options).then(xhr => {
    if (!condition(xhr)) {
      waitForPoll(route, condition, options)
    }
  })
}

function expectAndDismissToast(message) {
  cy.get('.toasted')
    .contains(message)
    .as('toastBody')
    .should('be.visible')
    .contains('OK')
    .click()
}

describe('tap-facebook', () => {
  beforeEach(() => {
    cy.server()

    cy.route('/api/v1/plugins/installed').as('getInstalledPlugins')
    cy.route('POST', '/api/v1/plugins/add').as('addPlugin')
    cy.route('/api/v1/orchestrations/extractors/tap-facebook/configuration').as(
      'getExtractorConfiguration'
    )
    cy.route('POST', '/api/v1/plugins/install').as('installPlugin')
    cy.route('POST', '/api/v1/plugins/install/batch').as(
      'installRelatedPlugins'
    )
    cy.route(
      'POST',
      '/api/v1/orchestrations/extractors/tap-facebook/configuration/test'
    ).as('testExtractorConfiguration')
    cy.route(
      'PUT',
      '/api/v1/orchestrations/extractors/tap-facebook/configuration'
    ).as('updateExtractorConfiguration')
    cy.route('POST', '/api/v1/orchestrations/pipeline-schedules').as(
      'createPipeline'
    )
    cy.route('POST', '/api/v1/orchestrations/run').as('runPipeline')
    cy.route('/api/v1/orchestrations/jobs/*/log').as('getJobLog')
    cy.route('POST', '/api/v1/orchestrations/jobs/state').as('getJobState')
  })

  it('can be configured', () => {
    cy.visit('/')

    cy.wait('@getInstalledPlugins')

    cy.get('[data-cy="tap-facebook-extractor-card"]')
      .contains('Connect')
      .click()

    cy.get('.modal')
      .as('modal')
      .should('be.visible')
      .should('contain', 'Connection Setup')

    cy.wait('@addPlugin')
    cy.wait('@getExtractorConfiguration')

    cy.get('@modal').within(() => {
      cy.get('h3')
        .contains('Configuration')
        .should('be.visible')

      cy.wait('@installPlugin', { responseTimeout: 60000 })
      // cy.wait('@installRelatedPlugins', { responseTimeout: 60000 })

      cy.get('button')
        .contains('Test Connection')
        .as('testConnectionButton')
        .should('be.enabled')
      cy.get('button.is-interactive-primary')
        .as('saveButton')
        .should('be.enabled')

      cy.get('@testConnectionButton').click()
    })

    cy.wait('@testExtractorConfiguration')

    expectAndDismissToast('Valid Extractor Connection')

    cy.get('@saveButton').click()

    cy.wait('@updateExtractorConfiguration')

    expectAndDismissToast('Connection saved')

    cy.wait('@createPipeline')

    expectAndDismissToast('Pipeline saved')

    cy.wait('@runPipeline')

    expectAndDismissToast('Auto running pipeline')

    cy.get('@modal')
      .should('be.visible')
      .should('contain', 'Run Log')

    waitForPoll(
      '@getJobLog',
      xhr => xhr.status == 200 && xhr.response.body.log.length > 0
    )

    cy.get('@modal').within(() => {
      cy.get('.modal-card-body-log').should(
        'contain',
        'Running extract & load...'
      )

      waitForPoll(
        '@getJobState',
        xhr => {
          const jobs = xhr.response.body.jobs
          return jobs.length > 0 && jobs[0].isComplete
        },
        { requestTimeout: 10000 }
      )

      cy.get('.modal-card-body-log')
        .should('contain', 'Extract & load complete!')
        .should('contain', 'Transformation complete!')

      cy.get('button.is-interactive-primary')
        .as('reportsButton')
        .should('be.enabled')

      cy.get('@reportsButton').click()

      cy.get('#dropdown-reports')
        .as('reportsDropdown')
        .should('be.visible')

      cy.get('@reportsDropdown')
        .get('button')
        .contains('Fb ads insights')
        .as('reportButton')
        .should('be.enabled')

      cy.get('@reportButton').click()
    })
  })
})
