<template>
  <div class="about-container">
    <div class="about-header">
      <h1 class="about-title">关于我们</h1>
      <div class="about-subtitle">连接资源，共建精彩</div>
    </div>
    
    <div class="about-content">
      <div class="about-section">
        <div class="section-icon">
          <i class="bi bi-collection-fill"></i>
        </div>
        <h2 class="section-title">本站介绍</h2>
        <p class="section-text">
          欢迎来到美漫资源共建平台，我们致力于为美漫爱好者提供一个便捷、高效、安全的资源分享平台。
        </p>
        
        <div class="feature-grid">
          <div class="feature-item">
            <div class="feature-icon">
              <i class="bi bi-bullseye"></i>
            </div>
            <h3>我们的使命</h3>
            <p>通过社区的力量，让优质资源得到更好的整理与传播，让每一位爱好者都能便捷地找到自己喜爱的内容。</p>
          </div>
          
          <div class="feature-item">
            <div class="feature-icon">
              <i class="bi bi-stars"></i>
            </div>
            <h3>我们的价值观</h3>
            <p><strong>开放共享</strong> - 鼓励用户分享优质资源<br>
              <strong>品质保证</strong> - 筛选审核每个资源内容<br>
              <strong>用户至上</strong> - 持续优化平台体验</p>
          </div>
          
          <div class="feature-item">
            <div class="feature-icon">
              <i class="bi bi-people-fill"></i>
            </div>
            <h3>我们的团队</h3>
            <p>我们是一群热爱动漫文化的技术爱好者，希望通过技术手段让资源分享变得更加简单高效。</p>
          </div>
        </div>
      </div>
      
      <div class="contact-section">
        <div class="contact-container">
          <div class="contact-left">
        <h2 class="section-title">联系我们</h2>
        <p class="section-text">
          如有任何问题、建议或合作意向，欢迎通过以下方式联系我们。我们非常重视每一位用户的反馈。
        </p>
        <div class="contact-methods">
          <div class="contact-item">
            <i class="bi bi-envelope-fill"></i>
                <span>admin@xueximeng.com</span>
          </div>
          <div class="contact-item">
                <i class="bi bi-github"></i>
                <span>GitHub: <a href="https://github.com/fish2018" target="_blank" style="color: white;">fish2018</a></span>
              </div>
            </div>
          </div>
          <div class="contact-right">
            <div class="decoration-circles">
              <div class="circle circle-1"></div>
              <div class="circle circle-2"></div>
              <div class="circle circle-3"></div>
            </div>
            <div class="contact-icon">
              <i class="bi bi-chat-text-fill"></i>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.about-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem 4rem;
}

.about-header {
  text-align: center;
  margin-bottom: 4rem;
  padding-bottom: 2.5rem;
  position: relative;
}

.about-header::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 4px;
  background: var(--primary-gradient);
  border-radius: 2px;
  box-shadow: 0 4px 10px rgba(99, 102, 241, 0.2);
}

.about-title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 1rem;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -1px;
}

.about-subtitle {
  font-size: 1.25rem;
  color: var(--gray-color);
  max-width: 600px;
  margin: 0 auto;
  letter-spacing: -0.2px;
}

.about-content {
  display: flex;
  flex-direction: column;
  gap: 3.5rem;
}

.about-section {
  background: rgba(255, 255, 255, 0.8);
  border-radius: var(--card-radius);
  padding: 3.5rem;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.06),
    inset 0 0 0 1px rgba(99, 102, 241, 0.1);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}

.about-section::before {
  content: '';
  position: absolute;
  top: -50px;
  right: -50px;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.07) 0%, transparent 70%);
  border-radius: 50%;
  z-index: 0;
}

.about-section:hover {
  transform: translateY(-5px);
  box-shadow: 
    0 30px 60px rgba(0, 0, 0, 0.1),
    inset 0 0 0 1px rgba(99, 102, 241, 0.2);
}

.section-icon {
  width: 80px;
  height: 80px;
  background: var(--primary-gradient);
  color: white;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  margin: 0 auto 2rem;
  box-shadow: 
    0 15px 30px rgba(99, 102, 241, 0.25),
    inset 0 2px 0 rgba(255, 255, 255, 0.3);
  position: relative;
  transform: rotate(-5deg);
  transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.about-section:hover .section-icon {
  transform: rotate(0deg) scale(1.05);
}

.section-title {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2rem;
  font-weight: 700;
  color: var(--dark-color);
  letter-spacing: -0.5px;
  position: relative;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 50px;
  height: 3px;
  background: var(--primary-gradient);
  border-radius: 3px;
}

.section-text {
  color: var(--gray-color);
  line-height: 1.8;
  text-align: center;
  font-size: 1.1rem;
  position: relative;
  z-index: 1;
  margin-bottom: 3rem;
}

.section-text strong {
  color: var(--dark-color);
  font-weight: 600;
}

/* 新增网格布局的特性展示 */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2.5rem;
  margin-top: 3rem;
}

.feature-item {
  background: rgba(255, 255, 255, 0.7);
  border-radius: var(--border-radius);
  padding: 2rem;
  transition: all 0.3s ease;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

.feature-item:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  border-color: rgba(99, 102, 241, 0.2);
}

.feature-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-gradient);
  color: white;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  margin-bottom: 1.5rem;
  box-shadow: 
    0 10px 20px rgba(99, 102, 241, 0.2),
    inset 0 2px 0 rgba(255, 255, 255, 0.3);
}

.feature-item h3 {
  font-size: 1.3rem;
  margin-bottom: 1rem;
  color: var(--dark-color);
  font-weight: 700;
}

.feature-item p {
  color: var(--gray-color);
  font-size: 1rem;
  line-height: 1.7;
}

/* 联系我们部分 */
.contact-section {
  background: var(--primary-gradient);
  color: white;
  border-radius: var(--card-radius);
  padding: 0;
  position: relative;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(99, 102, 241, 0.3);
}

.contact-container {
  display: flex;
  min-height: 400px;
}

.contact-left {
  flex: 1;
  padding: 3.5rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  z-index: 2;
}

.contact-right {
  flex: 0.8;
  position: relative;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.contact-icon {
  font-size: 8rem;
  color: rgba(255, 255, 255, 0.3);
  position: relative;
  z-index: 2;
  animation: pulse 3s infinite ease-in-out;
}

.decoration-circles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: -50px;
  right: -50px;
}

.circle-2 {
  width: 300px;
  height: 300px;
  bottom: -100px;
  right: -100px;
  background: rgba(255, 255, 255, 0.05);
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  left: -75px;
  background: rgba(255, 255, 255, 0.08);
}

.contact-section .section-title {
  color: white;
  margin-bottom: 2rem;
  text-align: left;
}

.contact-section .section-title::after {
  background: rgba(255, 255, 255, 0.3);
  left: 0;
  transform: none;
}

.contact-section .section-text {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2.5rem;
  text-align: left;
  font-size: 1.15rem;
}

.contact-methods {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  position: relative;
  z-index: 1;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: white;
  background: rgba(255, 255, 255, 0.15);
  padding: 1rem 1.75rem;
  border-radius: 100px;
  transition: all 0.3s;
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.contact-item:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-5px) translateX(8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.contact-item i {
  font-size: 1.3rem;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.5;
  }
}

/* 响应式设计 */
@media (max-width: 991px) {
  .about-title {
    font-size: 2.5rem;
  }
  
  .feature-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
  }
  
  .about-section {
    padding: 2.5rem;
  }
}

@media (max-width: 768px) {
  .contact-container {
    flex-direction: column;
  }
  
  .contact-right {
    height: 200px;
    order: -1;
  }
  
  .contact-left {
    padding: 2.5rem;
  }
  
  .feature-grid {
    grid-template-columns: 1fr;
  }
  
  .feature-item {
    padding: 1.5rem;
  }
}

@media (max-width: 576px) {
  .about-section {
    padding: 2rem 1.5rem;
  }
  
  .about-title {
    font-size: 2rem;
  }
  
  .contact-icon {
    font-size: 5rem;
  }
}
</style> 