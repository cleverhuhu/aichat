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
      timestamp: new Date()
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
/* Discord风格消息样式 */
.message-wrapper {
  display: flex;
  margin-bottom: 2px;
  padding: 2px 16px;
  transition: background-color 0.1s;
}

.message-wrapper:hover {
  background-color: #32353b;
}

/* 同一个发送者的连续消息，减少间距 */
.message-wrapper + .message-wrapper.ai-message,
.message-wrapper + .message-wrapper.user-message {
  margin-top: -20px;
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
  line-height: 1.5;
  word-wrap: break-word;
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
    padding: 2px 10px;
  }

  .message-avatar {
    width: 32px;
    height: 32px;
    margin-right: 10px;
  }
}
</style>