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
    cy.get('[data-cy="tap-carbon-intensity-extractor-card"]').within(() => {
      cy.get('.button')
        .contains('Install')
        .click({ force: true })
    })
    cy.wait('@installedPluginsApi')
    cy.wait('@addPluginsApi')
    cy.wait('@installPluginApi', {
      timeout: 60000
    })
    cy.wait('@carbonEntitiesApi')
  })

  it('A user can install target-sqlite', () => {
    cy.visit('/pipeline/load')
    cy.wait('@installedPluginsApi')
    cy.get('[data-cy="target-sqlite-loader-card"]').within(() => {
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
  })

  it('A user can skip the transform step', () => {
    cy.visit('/pipeline/transform')
    cy.get('[data-cy="save-transform"]')
      .contains('Save')
      .click({ force: true })
  })

  it('A user can schedule a new pipeline', () => {
    cy.route('POST', '/api/v1/orchestrations/pipeline_schedules').as(
      'pipelineSchedulesApi'
    )
    cy.route('POST', '/api/v1/orchestrations/run').as('runOrchestrationsApi')

    cy.visit('/pipeline/schedule')
    cy.get('[data-cy="create-pipeline-button"]').click({ force: true })
    cy.wait('@installedPluginsApi')
    cy.get('[data-cy="save-pipeline-button"]').click()
    cy.wait('@pipelineSchedulesApi')
    cy.wait('@runOrchestrationsApi')
    cy.contains('button', 'Analyze', {
      timeout: 60000
    })
      .should('not.be.disabled')
      .click({ force: true })
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
      '[data-cy="model-carbon-intensity-sqlite-carbon-model-card"]'
    ).within(() => {
      cy.get('.button')
        .contains('Analyze')
        .click()
    })
    cy.wait('@reportsApi')
    cy.wait('@getChartApi')
    cy.get('canvas').should('be.visible')
    cy.get('[data-cy="dropdown-save-report"]').click()
    cy.get('[data-cy="button-save-report"]').click()
    cy.wait('@saveReportsApi')
    cy.get('[data-cy="dropdown-add-to-dashboard"]').click()
    cy.get('[data-cy="button-new-dashboard"]').click()
    cy.get('[data-cy="button-create-dashboard"]').click()
    cy.wait('@saveDashboardApi')
    cy.wait('@addReportToDashboardApi')
    cy.visit('/dashboard')
    cy.get('[data-cy="dashboard-link"]:first-child').click()
    cy.get('canvas').should('be.visible')
  })
})
