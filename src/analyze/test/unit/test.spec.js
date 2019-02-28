import { mount } from '@vue/test-utils';
import repo from '../../src/api/repo';

test('works', () => {
  expect(mount).toBeInstanceOf(Function);
  expect(repo.index).toBeInstanceOf(Function);
});
