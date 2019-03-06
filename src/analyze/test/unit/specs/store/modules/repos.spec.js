import repos from '@/store/modules/repos';

describe('repos Vuex store', () => {
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

  test('hasMarkdown exists and is a function', () => {
    expect(repos.getters.hasMarkdown).toBeInstanceOf(Function);
  });

  test('hasCode exists and is a function', () => {
    expect(repos.getters.hasCode).toBeInstanceOf(Function);
  });
});
