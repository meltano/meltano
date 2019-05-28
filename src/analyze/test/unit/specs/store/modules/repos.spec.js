import repos from '@/store/modules/repos';

describe('repos Vuex store', () => {
  let state;

  beforeEach(() => {
    state = {
      activeView: { is_markdown: false, file: '', populated: false },
      loadingValidation: false,
      loadingUpdate: false,
      models: {},
      validated: false,
      errors: [],
      files: {},
    };
  });

  it('has the correct initial state', () => {
    expect(repos.state).toMatchObject(state);
  });

  it('validates that the hasMarkdown functions properly', () => {
    repos.state.activeView.is_markdown = true;
    repos.state.activeView.populated = true;

    expect(repos.getters.hasMarkdown()).toBe(true);

    repos.state.activeView.is_markdown = false;
    repos.state.activeView.populated = true;

    expect(repos.getters.hasMarkdown()).toBe(false);
  });

  it('validates that the hasCode functions properly', () => {
    repos.state.activeView.is_markdown = false;
    repos.state.activeView.populated = true;

    expect(repos.getters.hasCode()).toBe(true);

    repos.state.activeView.is_markdown = true;
    repos.state.activeView.populated = true;

    expect(repos.getters.hasCode()).toBe(false);
  });
});
