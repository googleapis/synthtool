/*!
 * Copyright 2019 Google LLC. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * Starts a static file server and run broken-link-checker.
 */

const http = require('http');

const send = require('send');
const parseUrl = require('parseurl');
const cp = require('child_process');

const PORT = 8080;
const PATH = `http://localhost:${PORT}`;
const DOCS_ROOT = './docs';

const command = 'blc';
const args = [
  PATH, '-r', '-o', '--exclude', 'www.googleapis.com',
].concat(process.argv.slice(2));

const checkBrokenLinks = server => {
  const cmd = cp.spawn(command, args);

  console.log(`Executing ${command} ${args.join(' ')}`);

  cmd.stdout.pipe(process.stdout);
  cmd.stderr.pipe(process.stderr);

  cmd.on('close', code => {
    server.close();
    if (code !== 0) {
      throw new Error('Broken links found, check output');
    };
  });
};

const server = http.createServer((req, res) => {
  send(req, parseUrl(req).pathname, {root: DOCS_ROOT}).pipe(res);
});

server.listen(PORT, (param) => {
  console.log(`Started http server on ${PATH}`);
  checkBrokenLinks(server);
});
