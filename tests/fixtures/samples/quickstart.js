/**
 * Copyright 2018, Google LLC
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

'use strict';

// [START bigtable_quickstart]
// Imports the Google Cloud client library
const Bigtable = require('@google-cloud/bigtable');

async function quickstart(
  INSTANCE_ID = 'my-instance', // ID of the Cloud Bigtable instance
  TABLE_ID = 'my-table' // ID of the Cloud Bigtable table
) {
  const bigtable = Bigtable();

  // Connect to an existing instance:my-bigtable-instance
  const instance = bigtable.instance(INSTANCE_ID);

  // Connect to an existing table:my-table
  const table = instance.table(TABLE_ID);

  // Read a row from my-table using a row key
  const [singleRow] = await table.row('r1').get();

  // Print the row key and data (column value, labels, timestamp)
  const rowData = JSON.stringify(singleRow.data, null, 4);
  console.log(`Row key: ${singleRow.id}\nData: ${rowData}`);
}
// [END bigtable_quickstart]

const args = process.argv.slice(2);
quickstart(...args).catch(console.error);
