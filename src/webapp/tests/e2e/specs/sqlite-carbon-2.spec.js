// https://docs.cypress.io/api/introduction/api.html

describe('Configuration', () => {
  it('A user can configure an installed plugin', () => {
    cy.server()
    cy.route('/api/v1/repos/models').as('modelsApi')
    cy.route('/api/v1/reports').as('reportsApi')

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

    cy.visit('http://localhost:8081/pipeline/schedule')
    cy.wait('@modelsApi')
    cy.get('.tag-running-pipelines').should('have.length', 0)
    cy.visit('http://localhost:8081/model')
    cy.wait('@modelsApi')
    cy.get(
      '[data-test-id="model-carbon-intensity-sqlite-carbon-model-card"]'
    ).within(() => {
      cy.get('.button')
        .contains('Analyze')
        .click()
    })
    cy.wait('@reportsApi')
    cy.get('[data-test-id="column-name"]').click()
    cy.get('[data-test-id="aggregate-count"]').click()
    cy.get('[data-test-id="run-query-button"]').click()
    cy.wait('@getChartApi')
    cy.get('canvas').should('be.visible')
    cy.get('[data-test-id="dropdown-save-report"]').click()
    cy.get('[data-test-id="button-save-report"]').click()
    cy.wait('@saveReportsApi')
    cy.get('[data-test-id="dropdown-add-to-dashboard"]').click()
    cy.get('[data-test-id="button-new-dashboard"]').click()
    cy.get('[data-test-id="button-create-dashboard"]').click()
    cy.wait('@saveDashboard')
    cy.wait('@addReport')
    cy.visit('http://localhost:8081/dashboard')
    cy.get('.dashboard-link:first-child').click()
    cy.wait('@dashboardReportsApi')
    cy.get('canvas').should('be.visible')
  })
})
