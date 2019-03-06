import repos from '@/store/modules/repos';

describe('repos Vuex store', () => {
  let state;

  beforeEach(() => {
    state = {
      activeView: { is_markdown: false, file: '', populated: false },
      loadingValidation: false,
      loadingUpdate: false,
      models: [],
      validated: false,
      navbarClicked: false,
      errors: [],
      files: {},
    };
  });

  it('has the correct initial state', () => {
    expect(repos.state).toMatchObject(state);
  });

  it('has the hasMarkdown function', () => {
    expect(repos.getters.hasMarkdown).toBeInstanceOf(Function);
  });

  it('validates the hasMarkdown function properly', () => {
    repos.state.activeView.is_markdown = true;
    repos.state.activeView.populated = true;
    expect(repos.getters.hasMarkdown()).toBe(true);

    repos.state.activeView.is_markdown = false;
    repos.state.activeView.populated = true;
    expect(repos.getters.hasMarkdown()).toBe(false);
  });

  it('has the hasCode function', () => {
    expect(repos.getters.hasCode).toBeInstanceOf(Function);
  });

  it('validates the hasCode function properly', () => {
    repos.state.activeView.is_markdown = false;
    repos.state.activeView.populated = true;
    expect(repos.getters.hasCode()).toBe(true);

    repos.state.activeView.is_markdown = true;
    repos.state.activeView.populated = true;
    expect(repos.getters.hasCode()).toBe(false);
  });
});
