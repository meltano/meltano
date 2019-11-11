describe('tap-carbon-intensity + target-sqlite', () => {
  beforeEach(() => {
    cy.server()

    cy.route('/api/v1/plugins/installed').as('installedPluginsApi')
    cy.route('POST', '/api/v1/plugins/add').as('addPluginsApi')
    cy.route('POST', '/api/v1/plugins/install').as('installPluginApi')
  })

  it('A user can install tap-carbon-intensity', () => {
    cy.route('POST', '/api/v1/orchestrations/entities/tap-carbon-intensity').as(
      'carbonEntitiesApi'
    )

    cy.visit('/')
    cy.wait('@installedPluginsApi')
    cy.get('[data-test-id="tap-carbon-intensity-extractor-card"]').within(
      () => {
        cy.get('.button')
          .contains('Install')
          .click({ force: true })
      }
    )
    cy.wait('@installedPluginsApi')
    cy.wait('@addPluginsApi')
    cy.wait('@installPluginApi', {
      timeout: 60000
    })
    cy.wait('@carbonEntitiesApi')
    cy.get('.modal-card-foot').within(() => {
      cy.get('.button')
        .contains('Save')
        .click({ force: true })
    })
  })

  it('A user can install target-sqlite', () => {
    cy.route('POST', '/api/v1/orchestrations/save/configuration').as(
      'saveConfigurationApi'
    )

    cy.visit('/pipeline/load')
    cy.wait('@installedPluginsApi')
    cy.get('[data-test-id="target-sqlite-loader-card"]').within(() => {
      cy.get('.button')
        .contains('Install')
        .click({ force: true })
    })
    cy.wait('@installedPluginsApi')
    cy.wait('@addPluginsApi')
    cy.wait('@installPluginApi', {
      timeout: 60000
    })
    cy.get('.modal-card-foot').within(() => {
      cy.get('.button')
        .contains('Save')
        .click({ force: true })
    })
    cy.wait('@saveConfigurationApi')
  })

  it('A user can skip the transform step', () => {
    cy.visit('/pipeline/transform')
    cy.get('[data-test-id="save-transform"]')
      .contains('Save')
      .click({ force: true })
  })

  it('A user can schedule a new pipeline', () => {
    cy.route('POST', '/api/v1/orchestrations/job/state').as('jobStateApi')

    cy.visit('/pipeline/schedule')
    cy.get('[data-cy="create-pipeline-button"]').click({ force: true })
    cy.wait('@installedPluginsApi')
    cy.get('[data-cy="save-pipeline-button"]').click()
    cy.wait('@jobStateApi', {
      timeout: 30000
    })
    cy.contains('button', 'Analyze', {
      timeout: 30000
    })
      .should('not.be.disabled')
      .click()
  })

  it('A user can analyze the data', () => {
    cy.route('/api/v1/reports').as('reportsApi')
    cy.route('/api/v1/repos/models').as('modelsApi')

    cy.route('POST', '/api/v1/dashboards/dashboard/save').as('saveDashboardApi')
    cy.route('POST', '/api/v1/dashboards/dashboard/report/add').as(
      'addReportToDashboardApi'
    )
    cy.route('POST', '/api/v1/dashboards/dashboard/reports').as(
      'dashboardReportsApi'
    )
    cy.route(
      'POST',
      '/api/v1/sql/get/model-carbon-intensity-sqlite/carbon/region'
    ).as('getChartApi')
    cy.route('POST', '/api/v1/reports/save').as('saveReportsApi')

    cy.visit('/model')
    cy.wait('@modelsApi')
    cy.get('.tag-running-pipelines').should('have.length', 0)
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
    cy.wait('@saveDashboardApi')
    cy.wait('@addReportToDashboardApi')
    cy.visit('/dashboard')
    cy.get('[data-test-id="dashboard-link"]:first-child').click()
    cy.wait('@dashboardReportsApi')
    cy.get('canvas').should('be.visible')
  })
})
