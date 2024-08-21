import { CompletedTaskSchemasPipe } from './completed-tasks.pipe';

describe('CompletedTaskSchemasPipe', () => {
  it('create an instance', () => {
    const pipe = new CompletedTaskSchemasPipe();
    expect(pipe).toBeTruthy();
  });
});
