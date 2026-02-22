#!/usr/bin/env node

/**
 * Tavily Search Script
 * Usage: node tavily-search.js "search query" [max_results]
 * 
 * Environment:
 *   TVLY_API_KEY - Tavily API key (required)
 */

const https = require('https');

const API_KEY = process.env.TVLY_API_KEY;
const BASE_URL = 'api.tavily.com';

if (!API_KEY) {
  console.error('Error: TVLY_API_KEY environment variable is not set');
  console.error('Please set it before running: export TVLY_API_KEY=your_key');
  process.exit(1);
}

function search(query, maxResults = 5) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({
      api_key: API_KEY,
      query: query,
      search_depth: 'basic',
      max_results: maxResults
    });

    const options = {
      hostname: BASE_URL,
      path: '/search',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const req = https.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          resolve(result);
        } catch (e) {
          reject(new Error('Failed to parse response: ' + e.message));
        }
      });
    });

    req.on('error', (e) => {
      reject(e);
    });

    req.write(postData);
    req.end();
  });
}

function formatResults(results) {
  if (!results || !results.results || results.results.length === 0) {
    return '未找到相关结果';
  }

  let output = `找到 ${results.results.length} 个结果：\n\n`;

  results.results.forEach((item, index) => {
    output += `### ${index + 1}. ${item.title}\n`;
    output += `**链接**: ${item.url}\n`;
    output += `**摘要**: ${item.content}\n`;
    if (item.score) {
      output += `**相关性**: ${(item.score * 100).toFixed(1)}%\n`;
    }
    output += '\n';
  });

  return output;
}

// Main
const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: node tavily-search.js "search query" [max_results]');
  console.error('Example: node tavily-search.js "OpenClaw AI" 5');
  process.exit(1);
}

const query = args[0];
const maxResults = args[1] ? parseInt(args[1], 10) : 5;

console.log(`搜索: ${query}`);
console.log(`最大结果数: ${maxResults}\n`);

search(query, maxResults)
  .then(results => {
    console.log(formatResults(results));
  })
  .catch(error => {
    console.error('搜索失败:', error.message);
    process.exit(1);
  });
