const fs = require('fs/promises');
const path = require('path');
const cp = require('child_process');
const yaml = require('js-yaml');


const LIBRARIAN_SCRIPT = 'librarian.js';
const README_PARTIALS = 'readme-partials.yaml';

async function checkFileExists(filePath) {
  try {
    // This attempts to check if the file exists.
    // If the file is not found, it throws an error.
    await fs.access(filePath);
    return true; // File exists
  } catch (error) {
    // We catch the expected 'file not found' error, and return false.
    // If a different error occurs (e.g., permission issues), it would still be caught.
    if (error.code === 'ENOENT') {
      return false; // File does not exist
    }
    // Re-throw the error if it's not a 'file not found' error.
    throw error;
  }
}


async function main(libraryDirectory) {
    const librarianCustomScriptPath = path.join(libraryDirectory, LIBRARIAN_SCRIPT);
    
    // Run any custom function the library provides
    if (await checkFileExists(librarianCustomScriptPath)) {
        console.log(`Running ${librarianCustomScriptPath}`);
        cp.execSync(`node ${librarianCustomScriptPath}`);
        console.log(`Successfully ${librarianCustomScriptPath}`);
    }

    const readMePartialsPath = path.join(libraryDirectory, README_PARTIALS);
    // Regenerate the README
    if (await checkFileExists(readMePartialsPath)) {
        const readmePartialsYaml = yaml.load(fs.readFileSync(readMePartialsPath, 'utf8'));
        console.log(`Regenerating README.md in ${libraryDirectory} with ${JSON.stringify(readMePartialsPath)}`);
        if (readmePartialsYaml.introduction) {
            cp.execSync(`generate-readme --library-path=${libraryDirectory}
                        --string-to-replace '[//]: # "partials.introduction"'
                        --replacement-string ${readmePartialsYaml.introduction}`);
        }
        if (readmePartialsYaml.body) {
            cp.execSync(`generate-readme --library-path=${libraryDirectory}
                        --string-to-replace '[//]: # "partials.body"'
                        --replacement-string ${readmePartialsYaml.body}`);
        }
        console.log('Finished regenerating README');  
    }

    console.log('Running npm fix');
    cp.execSync('npx gts fix', {cwd: libraryDirectory});
    console.log('Finished running npm');
}

main(...process.argv.slice(2));