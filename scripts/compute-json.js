const fs = require('fs');
const path = require('path');

const inputDir = './atomic-testings';
const outputFile = './indexes/full-payloads.json';

function aggregateJsonFilesPath(dirPath) {
  let filesList = [];

  fs.readdirSync(dirPath).forEach(file => {
    const fullPath = path.join(dirPath, file);
    const infoPath = fs.statSync(fullPath);

    if (infoPath.isDirectory()) {
      filesList = filesList.concat(aggregateJsonFilesPath(fullPath));
    } else if (path.extname(fullPath) === '.json') {
      filesList.push(fullPath);
    }
  });

  return filesList;
}

function computeJsonFiles() {
  const jsonFilesPath = aggregateJsonFilesPath(inputDir);
  let mergedData = [];

  jsonFilesPath.forEach(filePath => {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const jsonData = JSON.parse(content);
      mergedData.push(jsonData);
    } catch (error) {
      console.error(error.message);
    }
  });

  fs.writeFileSync(outputFile, JSON.stringify(mergedData, null, 2), 'utf8');
  console.log(`✅ Merge done : ${outputFile}`);
}

computeJsonFiles();
