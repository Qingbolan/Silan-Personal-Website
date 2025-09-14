#!/usr/bin/env node

/**
 * API调试工具
 * 诊断为什么前端没有向后端发送请求
 */

const API_BASE_URL = 'http://localhost:8888';

/**
 * 检查后端服务是否运行
 */
async function checkBackendStatus() {
  console.log('🔍 检查后端服务状态...\n');
  
  try {
    const response = await fetch(API_BASE_URL, { 
      method: 'GET',
      mode: 'cors' // 检查CORS
    });
    
    if (response.ok) {
      console.log('✅ 后端服务运行正常');
      console.log(`   状态码: ${response.status}`);
      console.log(`   URL: ${API_BASE_URL}`);
      return true;
    } else {
      console.log('❌ 后端服务响应异常');
      console.log(`   状态码: ${response.status}`);
      console.log(`   状态文本: ${response.statusText}`);
      return false;
    }
  } catch (error) {
    console.log('🔥 无法连接到后端服务');
    console.log(`   错误: ${error.message}`);
    console.log(`   类型: ${error.name}`);
    
    if (error.message.includes('ECONNREFUSED')) {
      console.log('\n💡 建议: 后端服务可能没有启动，请检查:');
      console.log('   1. 后端服务是否在运行');
      console.log('   2. 服务是否监听在 8888 端口');
      console.log('   3. 防火墙是否阻止了连接');
    }
    
    if (error.message.includes('CORS') || error.message.includes('cross-origin')) {
      console.log('\n💡 建议: 可能存在CORS跨域问题');
      console.log('   请确保后端配置了正确的CORS设置');
    }
    
    return false;
  }
}

/**
 * 测试具体的API端点
 */
async function testSpecificEndpoint(endpoint, description) {
  console.log(`\n🧪 测试端点: ${endpoint}`);
  console.log(`   描述: ${description}`);
  
  try {
    const url = `${API_BASE_URL}${endpoint}?lang=en`;
    console.log(`   完整URL: ${url}`);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
    });
    
    console.log(`   响应状态: ${response.status} ${response.statusText}`);
    console.log(`   响应头:`);
    response.headers.forEach((value, key) => {
      console.log(`     ${key}: ${value}`);
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log(`   响应数据类型: ${typeof data}`);
      console.log(`   数据键数: ${Object.keys(data || {}).length}`);
      console.log('   ✅ 请求成功');
    } else {
      const errorText = await response.text();
      console.log(`   错误响应: ${errorText}`);
      console.log('   ❌ 请求失败');
    }
    
  } catch (error) {
    console.log(`   异常: ${error.message}`);
    console.log('   🔥 连接失败');
  }
}

/**
 * 检查前端API调用逻辑
 */
function analyzeApiLogic() {
  console.log('\n📋 分析前端API调用逻辑...\n');
  
  console.log('🔧 当前API配置:');
  console.log(`   BASE_URL: http://localhost:8888`);
  console.log(`   超时时间: 10000ms`);
  console.log(`   默认头部: application/json`);
  
  console.log('\n⚠️  发现的潜在问题:');
  console.log('1. 🛡️ 使用了 withFallback 机制');
  console.log('   - API调用失败时会静默使用mock数据');
  console.log('   - 这可能隐藏了实际的网络错误');
  console.log('   - 建议临时禁用fallback来调试');
  
  console.log('\n2. 📡 请求发送检查:');
  console.log('   - 检查浏览器开发者工具的Network标签');
  console.log('   - 查看是否有实际的HTTP请求发出');
  console.log('   - 如果没有请求，可能API函数没有被调用');
  
  console.log('\n3. 🚫 可能的阻止原因:');
  console.log('   - 组件没有调用API函数');
  console.log('   - useEffect依赖数组问题');
  console.log('   - 条件渲染阻止了API调用');
  console.log('   - 错误处理吞噬了异常');
}

/**
 * 提供解决方案
 */
function provideSolutions() {
  console.log('\n🔧 解决方案建议:\n');
  
  console.log('1. 📊 启用详细日志:');
  console.log('```javascript');
  console.log('// 在API调用前添加');
  console.log('console.log("正在调用API:", endpoint);');
  console.log('');
  console.log('// 临时禁用fallback');
  console.log('return withFallback(apiCall, fallbackData, false); // 设为false');
  console.log('```');
  
  console.log('\n2. 🌐 检查浏览器控制台:');
  console.log('   - 按F12打开开发者工具');
  console.log('   - 查看Console标签的错误信息');
  console.log('   - 查看Network标签的请求记录');
  
  console.log('\n3. 🔄 重启服务:');
  console.log('   - 重启后端服务');
  console.log('   - 重启前端开发服务器');
  console.log('   - 清除浏览器缓存');
  
  console.log('\n4. 🧪 手动测试API:');
  console.log('```bash');
  console.log('# 测试后端是否运行');
  console.log('curl http://localhost:8888/api/v1/resume?lang=en');
  console.log('');
  console.log('# 或使用本脚本');
  console.log('node api_debug_tool.js');
  console.log('```');
}

/**
 * 主诊断流程
 */
async function runDiagnostics() {
  console.log('🚀 API调试诊断开始...\n');
  console.log('=' + '='.repeat(50));
  
  // 1. 检查后端服务
  const backendOk = await checkBackendStatus();
  
  if (backendOk) {
    // 2. 测试关键API端点
    await testSpecificEndpoint('/api/v1/resume', 'Resume API - 获取简历数据');
    await testSpecificEndpoint('/api/v1/projects', 'Projects API - 获取项目列表');
    await testSpecificEndpoint('/api/v1/ideas', 'Ideas API - 获取想法列表');
  }
  
  // 3. 分析前端逻辑
  analyzeApiLogic();
  
  // 4. 提供解决方案
  provideSolutions();
  
  console.log('\n' + '='.repeat(60));
  console.log('📋 诊断完成');
  console.log('='.repeat(60));
}

// 运行诊断
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
API调试工具使用说明:

基本用法:
  node api_debug_tool.js

功能:
  ✓ 检查后端服务状态
  ✓ 测试API端点连通性
  ✓ 分析前端API调用逻辑
  ✓ 提供问题解决方案

前提条件:
  - Node.js环境
  - 网络连接
  - 后端服务运行在 localhost:8888 (可选)
`);
  } else {
    runDiagnostics().catch(error => {
      console.error('\n❌ 诊断过程发生错误:', error);
      process.exit(1);
    });
  }
} 