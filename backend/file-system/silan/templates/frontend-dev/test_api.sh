#!/bin/bash

# API Test Script for Silan Personal Website API
# Base URL for the API server
BASE_URL="http://localhost:8888"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to make API calls and display results
test_api() {
    local method=$1
    local endpoint=$2
    local description=$3
    local params=$4
    
    echo -e "${BLUE}Testing: ${description}${NC}"
    echo -e "${YELLOW}Endpoint: ${method} ${endpoint}${NC}"
    
    if [ "$method" = "GET" ]; then
        if [ -n "$params" ]; then
            response=$(curl -s "${BASE_URL}${endpoint}?${params}")
        else
            response=$(curl -s "${BASE_URL}${endpoint}")
        fi
    fi
    
    # Check if response is valid JSON
    if echo "$response" | python -m json.tool > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Success${NC}"
        echo "$response" | python -m json.tool | head -n 20
        echo "..."
    else
        echo -e "${RED}✗ Failed or Invalid JSON${NC}"
        echo "Response: $response"
    fi
    echo "----------------------------------------"
    echo
}

echo -e "${BLUE}=== Silan Personal Website API Test Suite ===${NC}"
echo -e "${YELLOW}Base URL: ${BASE_URL}${NC}"
echo -e "${YELLOW}Database: api-test-portfolio/portfolio.db${NC}"
echo
echo "Starting API tests..."
echo

# ========== RESUME PAGE GROUP ==========
echo -e "${GREEN}========== RESUME PAGE GROUP ==========${NC}"

test_api "GET" "/api/v1/resume/" "Get complete resume data"
test_api "GET" "/api/v1/resume/" "Get complete resume data (Chinese)" "lang=zh"

test_api "GET" "/api/v1/resume/personal" "Get personal information"
test_api "GET" "/api/v1/resume/personal" "Get personal information (Chinese)" "lang=zh"

test_api "GET" "/api/v1/resume/education" "Get education list"
test_api "GET" "/api/v1/resume/education" "Get education list (Chinese)" "lang=zh"

test_api "GET" "/api/v1/resume/experience" "Get work experience list"
test_api "GET" "/api/v1/resume/experience" "Get work experience list (Chinese)" "lang=zh"

test_api "GET" "/api/v1/resume/research" "Get research projects list"
test_api "GET" "/api/v1/resume/research" "Get research projects list (Chinese)" "lang=zh"

test_api "GET" "/api/v1/resume/publications" "Get publications list"
test_api "GET" "/api/v1/resume/publications" "Get publications list (Chinese)" "lang=zh"

test_api "GET" "/api/v1/resume/awards" "Get awards list"
test_api "GET" "/api/v1/resume/awards" "Get awards list (Chinese)" "lang=zh"

test_api "GET" "/api/v1/resume/recent" "Get recent updates"
test_api "GET" "/api/v1/resume/recent" "Get recent updates (Chinese)" "lang=zh"

# ========== PROJECTS PAGE GROUP ==========
echo -e "${GREEN}========== PROJECTS PAGE GROUP ==========${NC}"

test_api "GET" "/api/v1/projects/" "Get projects list (default pagination)"
test_api "GET" "/api/v1/projects/" "Get projects list (page 1, size 5)" "page=1&size=5"
test_api "GET" "/api/v1/projects/" "Get projects list (Chinese)" "lang=zh"
test_api "GET" "/api/v1/projects/" "Get featured projects" "featured=true"
test_api "GET" "/api/v1/projects/" "Get projects by year" "year=2024"
test_api "GET" "/api/v1/projects/" "Search projects" "search=AI"

test_api "GET" "/api/v1/projects/categories" "Get project categories"
test_api "GET" "/api/v1/projects/categories" "Get project categories (Chinese)" "lang=zh"

test_api "GET" "/api/v1/projects/tags" "Get project tags"
test_api "GET" "/api/v1/projects/tags" "Get project tags (Chinese)" "lang=zh"

test_api "GET" "/api/v1/projects/graph" "Get project graph data"
test_api "GET" "/api/v1/projects/graph" "Get project graph data (Chinese)" "lang=zh"

test_api "GET" "/api/v1/projects/search" "Search project details"
test_api "GET" "/api/v1/projects/search" "Search project details with query" "query=machine learning"

# Test individual project endpoints (using sample IDs/slugs)
echo -e "${YELLOW}Testing individual project endpoints...${NC}"
test_api "GET" "/api/v1/projects/ai-chatbot" "Get project by slug"
test_api "GET" "/api/v1/projects/id/a31c2307-5aea-499a-85a2-caa7f1d24f08" "Get project by ID"
test_api "GET" "/api/v1/projects/a31c2307-5aea-499a-85a2-caa7f1d24f08/detail" "Get project detail"
test_api "GET" "/api/v1/projects/a31c2307-5aea-499a-85a2-caa7f1d24f08/blogs" "Get project related blogs"

# ========== ANNUAL PLANS GROUP ==========
echo -e "${GREEN}========== ANNUAL PLANS GROUP ==========${NC}"

test_api "GET" "/api/v1/plans/annual" "Get annual plans list"
test_api "GET" "/api/v1/plans/annual" "Get annual plans list (Chinese)" "lang=zh"

test_api "GET" "/api/v1/plans/annual/current" "Get current annual plan"
test_api "GET" "/api/v1/plans/annual/current" "Get current annual plan (Chinese)" "lang=zh"

test_api "GET" "/api/v1/plans/projects" "Get projects with plans"
test_api "GET" "/api/v1/plans/projects" "Get projects with plans (Chinese)" "lang=zh"

# Test specific plan endpoints
echo -e "${YELLOW}Testing specific plan endpoints...${NC}"
test_api "GET" "/api/v1/plans/annual/ziyun2024" "Get annual plan by name"
test_api "GET" "/api/v1/plans/ziyun2024/projects" "Get projects by plan name"

# ========== BLOG PAGE GROUP ==========
echo -e "${GREEN}========== BLOG PAGE GROUP ==========${NC}"

test_api "GET" "/api/v1/blog/posts" "Get blog posts list (default)"
test_api "GET" "/api/v1/blog/posts" "Get blog posts list (page 1, size 5)" "page=1&size=5"
test_api "GET" "/api/v1/blog/posts" "Get blog posts list (Chinese)" "lang=zh"
test_api "GET" "/api/v1/blog/posts" "Get featured blog posts" "featured=true"
test_api "GET" "/api/v1/blog/posts" "Search blog posts" "search=AI"

test_api "GET" "/api/v1/blog/categories" "Get blog categories"
test_api "GET" "/api/v1/blog/categories" "Get blog categories (Chinese)" "lang=zh"

test_api "GET" "/api/v1/blog/tags" "Get blog tags"
test_api "GET" "/api/v1/blog/tags" "Get blog tags (Chinese)" "lang=zh"

test_api "GET" "/api/v1/blog/search" "Search blog posts"
test_api "GET" "/api/v1/blog/search" "Search blog posts with query" "query=machine learning"

# Test individual blog endpoints
echo -e "${YELLOW}Testing individual blog endpoints...${NC}"
test_api "GET" "/api/v1/blog/posts/llm-code-refactoring" "Get blog post by slug"
test_api "GET" "/api/v1/blog/series/123e4567-e89b-12d3-a456-426614174000" "Get blog series data"

# ========== IDEAS PAGE GROUP ==========
echo -e "${GREEN}========== IDEAS PAGE GROUP ==========${NC}"

test_api "GET" "/api/v1/ideas/" "Get ideas list (default)"
test_api "GET" "/api/v1/ideas/" "Get ideas list (page 1, size 5)" "page=1&size=5"
test_api "GET" "/api/v1/ideas/" "Get ideas list (Chinese)" "lang=zh"
test_api "GET" "/api/v1/ideas/" "Get ideas by status" "status=active"
test_api "GET" "/api/v1/ideas/" "Search ideas" "search=quantum"

test_api "GET" "/api/v1/ideas/categories" "Get idea categories"
test_api "GET" "/api/v1/ideas/categories" "Get idea categories (Chinese)" "lang=zh"

test_api "GET" "/api/v1/ideas/tags" "Get idea tags"
test_api "GET" "/api/v1/ideas/tags" "Get idea tags (Chinese)" "lang=zh"

test_api "GET" "/api/v1/ideas/search" "Search ideas"
test_api "GET" "/api/v1/ideas/search" "Search ideas with query" "query=AI framework"

# Test individual idea endpoints
echo -e "${YELLOW}Testing individual idea endpoints...${NC}"
test_api "GET" "/api/v1/ideas/1" "Get idea by ID"
test_api "GET" "/api/v1/ideas/2" "Get idea by ID (2)"

# ========== COMPREHENSIVE TESTS ==========
echo -e "${GREEN}========== COMPREHENSIVE TESTS ==========${NC}"

echo -e "${YELLOW}Testing different parameter combinations...${NC}"

# Test pagination
test_api "GET" "/api/v1/projects/" "Projects - Page 2" "page=2&size=3"
test_api "GET" "/api/v1/blog/posts" "Blog Posts - Page 2" "page=2&size=3"
test_api "GET" "/api/v1/ideas/" "Ideas - Page 2" "page=2&size=3"

# Test filtering
test_api "GET" "/api/v1/projects/" "Projects - Filter by type" "type=web"
test_api "GET" "/api/v1/blog/posts" "Blog Posts - Filter by category" "category=technology"
test_api "GET" "/api/v1/ideas/" "Ideas - Filter by category" "category=AI"

# Test search functionality
test_api "GET" "/api/v1/projects/search" "Project Search - AI" "query=AI&lang=en"
test_api "GET" "/api/v1/blog/search" "Blog Search - Machine Learning" "query=machine learning&lang=en"
test_api "GET" "/api/v1/ideas/search" "Idea Search - Quantum" "query=quantum&lang=en"

echo -e "${GREEN}=== API Test Suite Completed ===${NC}"
echo -e "${YELLOW}Note: Some endpoints may fail if specific IDs/slugs don't exist in the database.${NC}"
echo -e "${YELLOW}This is expected behavior for testing purposes.${NC}" 