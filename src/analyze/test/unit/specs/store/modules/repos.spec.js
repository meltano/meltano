import repos from '@/store/modules/repos';

test('initial state is valid', () => {
  const state = {
    activeView: { is_markdown: false, file: '', populated: false },
    loadingValidation: false,
    loadingUpdate: false,
    models: [],
    validated: false,
    navbarClicked: false,
    errors: [],
    files: {},
  };

  expect(repos.state).toMatchObject(state);
});
