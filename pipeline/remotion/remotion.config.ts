import {Config} from '@remotion/cli/config';
// Use the headless Chromium that is already installed on this machine.
Config.setBrowserExecutable('/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell');
Config.setChromiumOpenGlRenderer('swangle');
