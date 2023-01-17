describe('Configuration', () => {
  it('A user can configure an installed plugin', () => {
    cy.server()
    cy.route('/pipeline/schedule').as('pipelineSchedulePage')
    cy.route('/api/v1/plugins/installed').as('installedApi')
    cy.route('/api/v1/orchestrations/pipeline_schedules').as(
      'pipelineSchedulesApi'
    )
    cy.route('POST', '/api/v1/plugins/add').as('addApi')
    cy.route('POST', '/api/v1/plugins/install').as('installApi')
    cy.route('POST', '/api/v1/orchestrations/entities/tap-carbon-intensity').as(
      'carbonEntitiesApi'
    )
    cy.route(
      'PUT',
      '/api/v1/orchestrations/extractors/tap-carbon-intensity/configuration'
    ).as('saveConfigurationApi')
    cy.route('POST', '/api/v1/orchestrations/jobs/state').as('jobStateApi')
    cy.route('POST', '/api/v1/orchestrations/run').as('runApi')

    cy.visit('/')
    cy.wait('@installedApi')
    cy.get('[data-test-id="tap-carbon-intensity-extractor-card"]').within(
      () => {
        cy.get('.button').contains('Install').click()
      }
    )
    cy.wait('@installedApi')
    cy.wait('@addApi')
    cy.wait('@installApi', {
      timeout: 60000,
    })
    cy.wait('@carbonEntitiesApi')
    cy.get('.modal-card-foot').within(() => {
      cy.get('.button').contains('Save').click()
    })
    cy.wait('@installedApi')
    cy.get('[data-test-id="target-sqlite-loader-card"]').within(() => {
      cy.get('.button').contains('Install').click()
    })
    cy.wait('@installedApi')
    cy.wait('@addApi')
    cy.wait('@installApi', {
      timeout: 60000,
    })
    cy.get('.modal-card-foot').within(() => {
      cy.get('.button').contains('Save').click()
    })
    cy.wait('@saveConfigurationApi')
    cy.get('[data-test-id="save-transform"]')
      .contains('Save')
      .click({ force: true })
    cy.wait('@pipelineSchedulesApi')
    cy.get('.modal-card-foot').within(() => {
      cy.get('.button').contains('Save').click()
    })
    cy.wait('@runApi')
    cy.get('.tag-running-pipelines').should('have.length', 1)
  })
})
