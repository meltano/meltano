describe('Usage data tracking', function() {
  it('Checks for Google Analytics', function() {
    cy.visit('/')
    cy.window().then(win => {
      expect(win.ga.loaded).to.be.true

      // GA is an acronym for Google Analytics
      expect(win.gaData).to.have.any.keys('UA-132758957-2')
    })
  })
})
