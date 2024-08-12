import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'unitPlural',
})
export class UnitPluralPipe implements PipeTransform {
  transform(value: string | undefined): string | undefined {
    if (!value) {
      return value;
    } else if (value == 'mile') {
      return 'miles'
    } else if (value == 'kilometer') {
      return 'kilometers'
    } else if (value == 'hour') {
      return 'hours'
    } else {
      return value;
    }
  }
}
