<template>
  <div class="message-wrapper" :class="{ 'user-message': message.type === 'user', 'ai-message': message.type === 'ai' }">
    <!-- 聊天头像 -->
    <div class="message-avatar" :style="avatarStyle"></div>

    <!-- 消息内容 -->
    <div class="message-content">
      <!-- 发送者名称 -->
      <div class="message-author" :class="{ 'user-author': message.type === 'user' }">
        {{ message.type === 'user' ? '你' : getCurrentCharacterName() }}
        <span class="message-time">{{ getFormattedTime() }}</span>
      </div>

      <!-- 图片（如果有） -->
      <div v-if="message.image" class="message-image">
        <img :src="message.image" alt="用户上传的图片" @click="openImagePreview(message.image)">
      </div>

      <!-- 消息文本 -->
      <div v-if="!message.loading" class="message-text">
        <div v-html="processedText"></div>
      </div>

      <!-- 加载指示器 -->
      <div v-else class="loading-indicator">
        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>

    <!-- 图片预览模态框 -->
    <div v-if="previewImage" class="image-preview-modal" @click="previewImage = null">
      <div class="image-preview-content">
        <img :src="previewImage" alt="图片预览">
        <button class="close-preview" @click.stop="previewImage = null">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    message: {
      type: Object,
      required: true,
    },
    aiAvatar: {
      type: String,
      default: null
    },
    userAvatar: {
      type: String,
      default: null
    }
  },

  data() {
    return {
      timestamp: new Date(),
      previewImage: null
    };
  },

  computed: {
    avatarStyle() {
      const avatar = this.message.type === 'user' ? this.userAvatar : this.aiAvatar;

      if (avatar) {
        return {
          backgroundImage: `url(${avatar})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        };
      }

      // 默认颜色头像
      return {
        backgroundColor: this.message.type === 'user' ? '#5865f2' : '#3ba55c'
      };
    },

    processedText() {
      if (!this.message.text) return '';

      // 处理引号内的文本为加粗，括号内的文本为斜体
      let text = this.message.text.replace(/[""]([^""]+)[""]/g, '<strong>$1</strong>');
      text = text.replace(/[（(]([^)）]+)[)）]/g, '<em>$1</em>');

      // 将换行符转换为<br>标签
      text = text.replace(/\n/g, '<br>');

      return text;
    }
  },

  methods: {

    openImagePreview(image) {
      this.previewImage = image;
    },


    getCurrentCharacterName() {
      // 尝试获取当前角色名称，如果无法获取，则使用默认值
      const selectedCharacter = this.$parent.settings?.selectedCharacter;
      if (selectedCharacter) {
        return selectedCharacter.split('.')[0];
      }
      return 'AI助手';
    },

    getFormattedTime() {
      const now = this.timestamp;
      const hours = now.getHours().toString().padStart(2, '0');
      const minutes = now.getMinutes().toString().padStart(2, '0');
      return `${hours}:${minutes}`;


    }
  }
};
</script>

<style scoped>

/* 消息中的图片 */
.message-image {
  margin-bottom: 8px;
  max-width: 250px;
}

.message-image img {
  max-width: 100%;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid #40444b;
}

/* 图片预览模态框 */
.image-preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.image-preview-content {
  position: relative;
  max-width: 90%;
  max-height: 90%;
}

.image-preview-content img {
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 4px;
}

.close-preview {
  position: absolute;
  top: -30px;
  right: 0;
  color: white;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
/* Discord风格消息样式 */
.message-wrapper {
  display: flex;
  margin-bottom: 8px; /* 增加下边距 */
  padding: 8px 16px; /* 增加上下内边距 */
  transition: background-color 0.1s;
}

.message-wrapper:hover {
  background-color: #32353b;
}

/* 同一个发送者的连续消息，减少间距但增加上下留白 */
.message-wrapper + .message-wrapper.ai-message,
.message-wrapper + .message-wrapper.user-message {
  margin-top: -4px; /* 减小上边距但保持一定间隔 */
}

.message-wrapper + .message-wrapper.ai-message .message-author,
.message-wrapper + .message-wrapper.user-message .message-author {
  display: none;
}

/* 头像样式 */
.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 16px;
  flex-shrink: 0;
  background-color: #5865f2;
  overflow: hidden;
}

/* 消息内容容器 */
.message-content {
  flex: 1;
  min-width: 0;
  padding-top: 2px;
}

/* 发送者名称 */
.message-author {
  font-size: 16px;
  font-weight: 500;
  color: white;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
}

.user-author {
  color: #5865f2;
}

/* 时间戳 */
.message-time {
  font-size: 12px;
  color: #72767d;
  margin-left: 8px;
  font-weight: 400;
}

/* 消息文本 */
.message-text {
  font-size: 15px;
  color: #dcddde;
  line-height: 1.6; /* 增加行高 */
  word-wrap: break-word;
  margin-bottom: 6px; /* 段落间距 */
}

/* 引用和动作样式 */
.message-text strong {
  color: #fff;
}

.message-text em {
  color: #a3a6aa;
  font-style: italic;
}

/* 加载指示器 */
.loading-indicator {
  padding: 8px 0;
}

.typing-indicator {
  display: flex;
  align-items: center;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #72767d;
  margin: 0 2px;
  animation: bounce 1.5s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-6px);
  }
}

/* 消息的进入动画 */
.message-wrapper {
  animation: messageSlideIn 0.2s ease-out;
  transform-origin: top;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .message-wrapper {
    padding: 6px 10px; /* 移动端保留一些内边距 */
  }

  .message-avatar {
    width: 32px;
    height: 32px;
    margin-right: 10px;
  }
}
</style>