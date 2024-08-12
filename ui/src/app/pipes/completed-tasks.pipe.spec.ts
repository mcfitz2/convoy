import { CompletedTasksPipe } from './completed-tasks.pipe';

describe('CompletedTasksPipe', () => {
  it('create an instance', () => {
    const pipe = new CompletedTasksPipe();
    expect(pipe).toBeTruthy();
  });
});
