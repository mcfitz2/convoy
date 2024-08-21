import { DueTaskSchemasPipe } from './due-tasks.pipe';

describe('DueTaskSchemasPipe', () => {
  it('create an instance', () => {
    const pipe = new DueTaskSchemasPipe();
    expect(pipe).toBeTruthy();
  });
});
