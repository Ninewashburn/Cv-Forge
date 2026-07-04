import { ChangeDetectionStrategy, Component } from '@angular/core';

import { Shell } from './layout/shell/shell';

@Component({
  selector: 'cvforge-root',
  imports: [Shell],
  templateUrl: './app.html',
  styleUrl: './app.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {}
