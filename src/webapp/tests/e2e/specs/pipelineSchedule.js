// https://docs.cypress.io/api/introduction/api.html

describe('Configuration', () => {
  it('A user can configure an installed plugin', () => {
    cy.server()
    cy.route('/pipeline/schedule').as('pipelineSchedulePage')
    cy.route('/api/v1/plugins/installed').as('installedApi')
    cy.route('/api/v1/orchestrations/get/pipeline_schedules').as(
      'pipelineSchedulesApi'
    )
    cy.route('POST', '/api/v1/plugins/add').as('addApi')
    cy.route('POST', '/api/v1/plugins/install').as('installApi')
    cy.route('POST', '/api/v1/orchestrations/entities/tap-carbon-intensity').as(
      'carbonEntitiesApi'
    )
    cy.route('POST', '/api/v1/orchestrations/save/configuration').as(
      'saveConfigurationApi'
    )
    cy.route('POST', '/api/v1/orchestrations/job/state').as('jobStateApi')
    cy.route('POST', '/api/v1/orchestrations/run').as('runApi')

    cy.visit('http://localhost:8080/pipeline/schedule')
    cy.wait('@pipelineSchedulesApi')
    cy.get('.buttons.is-right').within(() => {
      cy.get('.button')
        .contains('Run')
        .click()
    })
    cy.wait('@runApi')
    cy.get('.tag-running-pipelines').should('have.length', 1)
    cy.wait('@jobStateApi', {
      timeout: 10000
    })
    cy.get('.tag-running-pipelines').should('have.length', 0)
  })
})
