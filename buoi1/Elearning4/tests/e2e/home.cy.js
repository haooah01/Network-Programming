describe('Home Page', () => {
  it('should display welcome message', () => {
    cy.visit('/')
    cy.contains('Welcome to Vue App')
  })
})