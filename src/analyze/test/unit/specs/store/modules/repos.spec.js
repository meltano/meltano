import repos from '@/store/modules/repos';

describe('repos Vuex store', () => {
  let initialState;

  beforeEach(() => {
    initialState = {
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
    expect(repos.state).toMatchObject(initialState);
  });

  it('validates that the hasMarkdown functions properly', () => {
    const { activeView } = repos.state;

    activeView.is_markdown = true;
    activeView.populated = true;
    expect(repos.getters.hasMarkdown()).toBe(true);

    activeView.is_markdown = false;
    activeView.populated = true;
    expect(repos.getters.hasMarkdown()).toBe(false);
  });

  it('validates that the hasCode functions properly', () => {
    const { activeView } = repos.state;

    activeView.is_markdown = false;
    activeView.populated = true;
    expect(repos.getters.hasCode()).toBe(true);

    activeView.is_markdown = true;
    activeView.populated = true;
    expect(repos.getters.hasCode()).toBe(false);
  });
});
