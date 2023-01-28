describe('Usage data tracking', function () {
  it('Checks for Google Analytics', function () {
    cy.visit('/')
    cy.window().then((win) => {
      // GA is an acronym for Google Analytics
      const appGAId = Object.keys(win.gaData)[0]
      const meltanoGAId = 'UA-132758957-2'

      expect(appGAId).to.equal(meltanoGAId)
    })
  })
})
