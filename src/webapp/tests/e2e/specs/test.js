// https://docs.cypress.io/api/introduction/api.html

describe('Configuration', () => {
  it('A user can configure an installed plugin', () => {
    cy.server()
    cy.route('/api/v1/plugins/installed').as('api')

    cy.visit('http://localhost:8080/')
    cy.wait('@api')
    cy.get('.tile.is-child').within(() => {
      cy.get('.button')
        .contains('Configure')
        .click()
    })
  })
})
