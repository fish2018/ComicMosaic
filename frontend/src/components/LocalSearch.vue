<template>
  <div class="header-search-container">
    <!-- 搜索框 -->
    <div class="search-wrapper" :class="{ 'active': isSearchActive || searchText }">
      <div class="search-box">
        <i class="bi bi-search search-icon"></i>
        <input 
          type="text" 
          class="search-input" 
          :placeholder="resources.length > 0 ? '搜索资源...' : '资源加载中...'" 
          v-model="searchText"
          @focus="isSearchActive = true"
          @blur="handleBlur"
          @input="performSearch"
          @keydown.esc="clearSearch"
          :disabled="resources.length === 0"
        />
        <button v-if="searchText" class="clear-btn" @click="clearSearch">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </div>
    
    <!-- 搜索结果弹出框 -->
    <div v-if="searchText && filteredResources.length > 0" class="search-results-popup">
      <div class="results-header">
        <h3 class="results-title">
          找到 {{ filteredResources.length }} 个结果
        </h3>
        <button class="close-results-btn" @click="clearSearch" title="关闭结果">
          <i class="bi bi-x"></i>
        </button>
      </div>
      
      <div class="results-list">
        <div 
          v-for="resource in filteredResources.slice(0, 5)" 
          :key="resource.id" 
          class="result-item"
          @click="goToDetail(resource.id)"
        >
          <div class="result-image">
            <img 
              :src="getPosterImage(resource)" 
              :alt="resource.title || resource.title_en" 
              loading="lazy"
            />
          </div>
          <div class="result-info">
            <h4 class="result-title">
              {{ resource.title || resource.title_en }}
            </h4>
            <p v-if="resource.title && resource.title_en" class="result-subtitle">{{ resource.title_en }}</p>
            <div class="result-tags">
              <span 
                v-for="(type, index) in getResourceTypes(resource)" 
                :key="index"
                class="result-tag"
              >
                {{ type }}
              </span>
            </div>
          </div>
        </div>
        
        <!-- 显示更多结果链接 -->
        <div v-if="filteredResources.length > 5" class="more-results">
          <button class="more-btn" @click="showAllResults">
            <i class="bi bi-list"></i>
            查看全部 {{ filteredResources.length }} 个结果
          </button>
        </div>
      </div>
    </div>
    
    <!-- 空结果弹出框 -->
    <div v-else-if="searchText && filteredResources.length === 0" class="search-results-popup empty-results">
      <div class="empty-results-content">
        <i class="bi bi-search"></i>
        <p>未找到"{{ searchText }}"相关资源</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  resources: {
    type: Array,
    default: () => []
  }
})

const router = useRouter()
const searchText = ref('')
const isSearchActive = ref(false)

// 搜索防抖
let debounceTimeout = null
const performSearch = () => {
  if (debounceTimeout) {
    clearTimeout(debounceTimeout)
  }
  
  debounceTimeout = setTimeout(() => {
    // 搜索已经在计算属性中自动处理
  }, 300)
}

// 过滤资源（默认搜索所有字段）
const filteredResources = computed(() => {
  if (!searchText.value) return []
  
  const searchTerms = searchText.value.toLowerCase().split(' ').filter(term => term)
  if (searchTerms.length === 0) return []
  
  return props.resources.filter(resource => {
    // 检查每个搜索词是否匹配任何字段
    return searchTerms.every(term => {
      return (
        (resource.title && resource.title.toLowerCase().includes(term)) ||
        (resource.title_en && resource.title_en.toLowerCase().includes(term)) ||
        (resource.description && resource.description.toLowerCase().includes(term))
      )
    })
  })
})

// 跳转到资源详情
const goToDetail = (id) => {
  router.push(`/resource/${id}`)
  clearSearch()
}

// 显示全部搜索结果
const showAllResults = () => {
  // 实现方式：可以通过路由导航到一个搜索结果页面
  // 也可以打开一个模态框展示全部结果
  // 暂时先清除搜索
  clearSearch()
}

// 显示资源的标签
const getResourceTypes = (resource) => {
  if (!resource.resource_type) return []
  return resource.resource_type.split(',').slice(0, 2) // 最多显示2个标签
}

// 获取海报图片
const getPosterImage = (resource) => {
  if (resource.poster_image) {
    return resource.poster_image
  } else if (resource.images && resource.images.length > 0) {
    return resource.images[0]
  } else {
    return 'https://via.placeholder.com/300x400'
  }
}

// 清除搜索
const clearSearch = () => {
  searchText.value = ''
}

// 处理失焦
const handleBlur = () => {
  // 延迟关闭搜索状态
  setTimeout(() => {
    if (!searchText.value) {
      isSearchActive.value = false
    }
  }, 200)
}

// 监听资源数据变化
watch(() => props.resources, (newResources) => {
  if (newResources.length > 0) {
    console.log('本地搜索组件收到资源数据，共', newResources.length, '条')
  }
}, { deep: true })

// 初始化时检查是否有数据
onMounted(() => {
  document.addEventListener('click', (event) => {
    const container = document.querySelector('.header-search-container')
    if (container && !container.contains(event.target)) {
      isSearchActive.value = false
    }
  })
  
  // 添加日志以便调试
  console.log('本地搜索组件挂载完成，资源数量:', props.resources.length)
})
</script>

<style scoped>
.header-search-container {
  position: relative;
  width: 320px;
  z-index: 150;
  transition: all 0.3s ease;
}

.header-search-container:hover {
  width: 350px;
}

/* 搜索框样式 */
.search-wrapper {
  margin-left: 1.3rem;
  position: relative;
  width: 95%;
  transition: width 0.3s ease;
}

.search-wrapper.active {
  width: 100%;
}

.search-box {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.3);  
  border-radius: 100px;
  padding: 0.48rem 0.85rem;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
}

.search-box:hover {
  background: rgba(255, 255, 255, 0.4);
  box-shadow: 0 6px 15px rgba(124, 58, 237, 0.2), 0 0 0 1px rgba(124, 58, 237, 0.3);
  transform: translateY(-2px);
  border-color: rgba(124, 58, 237, 0.4);
  backdrop-filter: blur(10px);
}

.search-wrapper.active .search-box {
  background: rgba(255, 255, 255, 0.95);
  border-color: var(--primary-color);
  box-shadow: 0 5px 20px rgba(124, 58, 237, 0.25), 0 0 0 2px rgba(124, 58, 237, 0.2);
}

.search-icon {
  color: rgba(255, 255, 255, 1);
  font-size: 1.05rem;
  margin-right: 0.5rem;
  transition: color 0.3s ease;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.search-wrapper.active .search-icon {
  color: var(--primary-color);
  text-shadow: none;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 0.95rem;
  color: white;
  padding: 0.25rem;
  width: 100%;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  font-weight: 500;
}

.search-wrapper.active .search-input {
  color: var(--dark-color);
  text-shadow: none;
}

.search-input:focus {
  outline: none;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.85);
  opacity: 0.85;
}

.search-wrapper.active .search-input::placeholder {
  color: var(--gray-color);
}

.search-input:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.clear-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.85);
  cursor: pointer;
  padding: 0.25rem;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.search-wrapper.active .clear-btn {
  color: var(--gray-color);
  text-shadow: none;
}

.clear-btn:hover {
  color: var(--accent-color);
}

/* 搜索结果弹出框 */
.search-results-popup {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 100%;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  z-index: 100;
  max-height: 500px;
  overflow-y: auto;
  animation: slideDown 0.3s ease forwards;
  /* 优化渲染性能 */
  will-change: transform, opacity;
  transform: translateZ(0);
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  -webkit-overflow-scrolling: touch;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.results-title {
  font-size: 0.9rem;
  margin: 0;
  color: var(--gray-color);
  font-weight: 600;
}

.close-results-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--gray-color);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-results-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--accent-color);
}

.results-list {
  padding: 0.5rem;
}

.result-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  margin-bottom: 0.5rem;
  /* 优化布局计算 */
  will-change: transform;
  transform: translateZ(0);
  contain: layout;
}

.result-item:hover {
  background-color: rgba(124, 58, 237, 0.05);
}

.result-image {
  width: 50px;
  height: 70px;
  margin-right: 1rem;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

.result-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  /* 预加载图片尺寸，防止渲染闪烁 */
  content-visibility: auto;
  contain: strict;
}

.result-info {
  flex: 1;
}

.result-title {
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0 0 0.25rem;
  color: var(--dark-color);
  line-height: 1.3;
}

.result-subtitle {
  font-size: 0.8rem;
  color: var(--gray-color);
  margin: 0 0 0.5rem;
}

.result-tags {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.result-tag {
  background: rgba(124, 58, 237, 0.1);
  color: var(--primary-color);
  padding: 0.15rem 0.5rem;
  border-radius: 100px;
  font-size: 0.7rem;
  font-weight: 600;
}

.more-results {
  text-align: center;
  padding: 0.75rem 0;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.more-btn {
  background: transparent;
  border: none;
  color: var(--primary-color);
  font-weight: 600;
  font-size: 0.85rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin: 0 auto;
}

.more-btn:hover {
  background: rgba(124, 58, 237, 0.1);
  border-radius: 100px;
}

/* 空结果样式 */
.empty-results {
  width: 100%;
}

.empty-results-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  color: var(--gray-color);
}

.empty-results-content i {
  font-size: 2rem;
  margin-bottom: 0.75rem;
  opacity: 0.5;
}

.empty-results-content p {
  margin: 0;
  font-size: 0.9rem;
}

/* 动画 */
@keyframes slideDown {
  from { 
    opacity: 0;
    transform: translateY(-10px); 
  }
  to { 
    opacity: 1;
    transform: translateY(0); 
  }
}

/* 为搜索框添加脉冲动画效果 */
@keyframes subtle-pulse {
  0% { box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(255, 255, 255, 0.6); }
  50% { box-shadow: 0 5px 15px rgba(124, 58, 237, 0.15), 0 0 0 1px rgba(124, 58, 237, 0.3); }
  100% { box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(255, 255, 255, 0.6); }
}

/* 当页面加载时显示一次脉冲效果，然后每隔30秒轻微闪烁一次 */
.search-box {
  animation: subtle-pulse 2s ease-in-out 1s, subtle-pulse 3s ease-in-out 30s infinite;
}

/* 响应式样式 */
@media (max-width: 992px) {
  .header-search-container {
    width: 250px;
  }
  
  .header-search-container:hover {
    width: 280px;
  }
}

@media (max-width: 768px) {
  .header-search-container {
    width: 40px;
    overflow: hidden;
    transition: all 0.45s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  
  .header-search-container:hover,
  .header-search-container:focus-within {
    width: 220px;
    overflow: visible;
  }
  
  .header-search-container:focus-within .search-box {
    background: rgba(255, 255, 255, 0.95);
    border-color: var(--primary-color);
    box-shadow: 0 5px 20px rgba(124, 58, 237, 0.3), 0 0 0 2px rgba(124, 58, 237, 0.2);
    transform: translateY(-4px) scale(1.02);
  }
  
  .header-search-container:focus-within .search-icon {
    color: var(--primary-color);
    text-shadow: none;
    animation: pulse 1s infinite;
  }
  
  @keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.2); }
    100% { transform: scale(1); }
  }
  
  .search-box {
    padding: 0.35rem;
    width: 40px;
    justify-content: center;
  }
  
  .header-search-container:hover .search-box,
  .header-search-container:focus-within .search-box {
    width: auto;
    padding: 0.35rem 0.75rem;
    justify-content: flex-start;
  }
  
  .search-icon {
    margin-right: 0;
  }
  
  .header-search-container:hover .search-icon,
  .header-search-container:focus-within .search-icon {
    margin-right: 0.5rem;
  }
  
  .search-input {
    width: 0;
    padding: 0;
  }
  
  .header-search-container:hover .search-input,
  .header-search-container:focus-within .search-input {
    width: 100%;
    padding: 0.25rem;
  }
  
  /* 搜索结果弹出框在移动设备上的样式 */
  .search-results-popup {
    width: 100%;
    right: 0;
    max-height: 400px;
  }
  
  .result-image {
    contain: strict;
    content-visibility: auto;
  }
}

/* 小屏幕手机 */
@media (max-width: 480px) {
  .header-search-container {
    margin-left: auto;
  }
  
  .header-search-container:hover,
  .header-search-container:focus-within {
    width: 180px;
  }
  
  .search-results-popup {
    width: 100%;
    right: 0;
  }
  
  .result-item {
    padding: 0.5rem;
  }
  
  .result-image {
    width: 40px;
    height: 60px;
    margin-right: 0.75rem;
  }
}
</style> 