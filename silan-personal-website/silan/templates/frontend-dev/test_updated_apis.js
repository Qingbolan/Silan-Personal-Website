#!/usr/bin/env node

/**
 * API端点测试脚本
 * 验证所有更新后的API是否正确指向后端接口
 */

const API_BASE_URL = 'http://localhost:8888';

// 所有API端点列表（与backend.api对应）
const API_ENDPOINTS = {
  resume: [
    'GET /api/v1/resume',
    'GET /api/v1/resume/personal',
    'GET /api/v1/resume/education', 
    'GET /api/v1/resume/experience',
    'GET /api/v1/resume/research',
    'GET /api/v1/resume/publications',
    'GET /api/v1/resume/awards',
    'GET /api/v1/resume/recent'
  ],
  projects: [
    'GET /api/v1/projects',
    'GET /api/v1/projects/:slug',
    'GET /api/v1/projects/id/:id',
    'GET /api/v1/projects/:id/detail',
    'GET /api/v1/projects/categories',
    'GET /api/v1/projects/tags',
    'GET /api/v1/projects/graph',
    'GET /api/v1/projects/:id/blogs',
    'GET /api/v1/projects/search'
  ],
  plans: [
    'GET /api/v1/plans/annual',
    'GET /api/v1/plans/annual/current',
    'GET /api/v1/plans/annual/:name',
    'GET /api/v1/plans/projects',
    'GET /api/v1/plans/:plan_name/projects'
  ],
  blog: [
    'GET /api/v1/blog/posts',
    'GET /api/v1/blog/posts/:slug',
    'GET /api/v1/blog/categories',
    'GET /api/v1/blog/tags',
    'GET /api/v1/blog/series/:series_id',
    'GET /api/v1/blog/search'
  ],
  ideas: [
    'GET /api/v1/ideas',
    'GET /api/v1/ideas/:id',
    'GET /api/v1/ideas/categories',
    'GET /api/v1/ideas/tags',
    'GET /api/v1/ideas/search'
  ]
};

/**
 * 测试API端点是否可访问
 */
async function testApiEndpoint(endpoint) {
  const url = `${API_BASE_URL}${endpoint.replace(/:\w+/g, 'test')}?lang=en`;
  
  try {
    console.log(`Testing: ${endpoint}`);
    const response = await fetch(url);
    
    if (response.ok) {
      console.log(`✅ ${endpoint} - Status: ${response.status}`);
      return { endpoint, status: 'success', code: response.status };
    } else {
      console.log(`❌ ${endpoint} - Status: ${response.status}`);
      return { endpoint, status: 'error', code: response.status };
    }
  } catch (error) {
    console.log(`🔥 ${endpoint} - Connection Error: ${error.message}`);
    return { endpoint, status: 'connection_error', error: error.message };
  }
}

/**
 * 测试所有API端点
 */
async function testAllEndpoints() {
  console.log('🚀 开始测试所有API端点...\n');
  
  const results = {
    total: 0,
    success: 0,
    error: 0,
    connection_error: 0,
    details: {}
  };

  for (const [category, endpoints] of Object.entries(API_ENDPOINTS)) {
    console.log(`\n📁 测试 ${category.toUpperCase()} API:`);
    console.log('=' + '='.repeat(50));
    
    results.details[category] = [];
    
    for (const endpoint of endpoints) {
      const path = endpoint.replace(/^GET\s+/, '');
      const result = await testApiEndpoint(path);
      
      results.details[category].push(result);
      results.total++;
      results[result.status]++;
      
      // 避免请求太快
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log('📊 测试结果汇总:');
  console.log('='.repeat(60));
  console.log(`总计: ${results.total} 个端点`);
  console.log(`✅ 成功: ${results.success} 个`);
  console.log(`❌ 错误: ${results.error} 个`);
  console.log(`🔥 连接失败: ${results.connection_error} 个`);
  
  if (results.success === results.total) {
    console.log('\n🎉 所有API端点都正常工作！');
  } else {
    console.log('\n⚠️  部分API端点存在问题，请检查后端服务是否正常运行。');
  }

  return results;
}

/**
 * 显示使用说明
 */
function showUsage() {
  console.log(`
📋 API端点测试脚本使用说明:

运行测试:
  node test_updated_apis.js

前提条件:
  1. 后端服务运行在 http://localhost:8888
  2. 后端实现了 backend.api 中定义的所有端点

测试内容:
  ✓ Resume API (8个端点)
  ✓ Projects API (9个端点)  
  ✓ Plans API (5个端点)
  ✓ Blog API (6个端点)
  ✓ Ideas API (5个端点)
  
  总计: ${Object.values(API_ENDPOINTS).flat().length} 个API端点

注意: 此脚本仅测试端点可访问性，不验证数据内容。
`);
}

// 主程序
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    showUsage();
  } else {
    testAllEndpoints().catch(error => {
      console.error('❌ 测试过程中发生错误:', error);
      process.exit(1);
    });
  }
}

module.exports = { testAllEndpoints, API_ENDPOINTS }; 