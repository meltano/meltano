// https://docs.cypress.io/api/introduction/api.html

describe('Configuration', () => {
  it('A user can configure an installed plugin', () => {
    cy.server()
    cy.route('/pipeline/schedule').as('pipelineSchedulePage')
    cy.route('/api/v1/plugins/installed').as('installedApi')
    cy.route('/api/v1/orchestrations/get/pipeline_schedules').as(
      'pipelineSchedulesApi'
    )
    cy.route('/api/v1/repos/models').as('modelsApi')
    cy.route('/api/v1/reports').as('reportsApi')

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
    cy.route(
      'POST',
      '/api/v1/sql/get/model-carbon-intensity-sqlite/carbon/region'
    ).as('getChartApi')
    cy.route('POST', '/api/v1/dashboards/dashboard/save').as('saveDashboard')
    cy.route('POST', '/api/v1/dashboards/dashboard/report/add').as('addReport')
    cy.route('POST', '/api/v1/reports/save').as('saveReportsApi')
    cy.route('POST', '/api/v1/dashboards/dashboard/reports').as(
      'dashboardReportsApi'
    )

    cy.visit('http://localhost:8080/pipeline/schedule')
    cy.wait('@modelsApi')
    cy.get('.tag-running-pipelines').should('have.length', 0)
    cy.visit('http://localhost:8080/model')
    cy.wait('@modelsApi')
    cy.get('#model-carbon-intensity-sqlite-carbon-model-card').within(() => {
      cy.get('.button')
        .contains('Analyze')
        .click()
    })
    cy.wait('@reportsApi')
    cy.get('#column-name').click()
    cy.get('#aggregate-count').click()
    cy.get('#run-query-button').click()
    cy.wait('@getChartApi')
    cy.get('canvas').should('be.visible')
    cy.get('#dropdown-save-report').click()
    cy.get('#button-save-report').click()
    cy.wait('@saveReportsApi')
    cy.get('#dropdown-add-to-dashboard').click()
    cy.get('#button-new-dashboard').click()
    cy.get('#button-create-dashboard').click()
    cy.wait('@saveDashboard')
    cy.wait('@addReport')
    cy.visit('http://localhost:8080/dashboard')
    cy.get('.dashboard-link:first-child').click()
    cy.wait('@dashboardReportsApi')
    cy.get('canvas').should('be.visible')
  })
})
