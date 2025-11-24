Cypress.Commands.add('login', () => {
  cy.fixture('testuser.json').then(({ username, password }) => {
    // We need to request a page that sets the csrf cookie
    cy.request('/api/v2/instance/nodeinfo/2.1/')

    cy.getCookie('csrftoken').then(($cookie) => {
      cy.request({
        method: 'POST',
        url: '/api/v2/users/login',
        form: true,
        headers: {
          'X-CSRFTOKEN': $cookie?.value,
          Referer: Cypress.config().baseUrl + '/login'
        },
        body: {
          username,
          password
        }
      })
    })
  })
})
