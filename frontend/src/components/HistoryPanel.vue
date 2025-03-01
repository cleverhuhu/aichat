<template>
  <div class="history-panel" :class="{ 'open': isOpen }">
    <div class="history-toggle" @click="togglePanel">
      <div class="toggle-icon">
        <span class="material-icon">{{ isOpen ? '&#xe5c8;' : '&#xe5c7;' }}</span>
      </div>
    </div>

    <div class="history-content">
      <div class="history-header">
        <h3>
          <span class="material-icon">&#xe889;</span>
          聊天记录
        </h3>
        <button @click="createNewChat" class="new-chat-btn">
          <span class="material-icon">&#xe145;</span>
          新建聊天
        </button>
      </div>

      <div class="history-filters">
        <div class="search-box">
          <span class="material-icon search-icon">&#xe8b6;</span>
          <input type="text" v-model="searchQuery" placeholder="搜索聊天记录..." />
          <span v-if="searchQuery" @click="searchQuery = ''" class="material-icon clear-icon">&#xe5cd;</span>
        </div>

        <div class="filter-options">
          <select v-model="filterCharacter" class="filter-select">
            <option value="">所有角色</option>
            <option v-for="character in uniqueCharacters" :key="character" :value="character">
              {{ character }}
            </option>
          </select>
        </div>
      </div>

      <div class="history-list">
        <div v-if="isLoading" class="loading-history">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>

        <div v-else-if="filteredHistoryFiles.length === 0" class="empty-history">
          <div class="empty-icon">
            <span class="material-icon">&#xe880;</span>
          </div>
          <p>{{ searchQuery || filterCharacter ? '没有找到匹配的聊天记录' : '暂无聊天记录' }}</p>
          <button v-if="searchQuery || filterCharacter" @click="clearFilters" class="clear-filters-btn">
            清除筛选
          </button>
        </div>

        <div v-else class="history-items">
          <div
            v-for="(file, index) in filteredHistoryFiles"
            :key="index"
            class="history-item"
            :class="{ 'active': selectedHistory === file.id }"
            @click="selectHistory(file.id)">
            <div class="history-item-avatar">
              <div v-if="file.character_avatar" class="avatar-image" :style="{ backgroundImage: `url(${file.character_avatar})` }"></div>
              <div v-else class="avatar-placeholder">{{ getInitials(file.character) }}</div>
            </div>

            <div class="history-item-content">
              <div class="history-title">{{ formatHistoryName(file.name) }}</div>
              <div class="history-info">
                <span class="history-character">{{ file.character || '未知角色' }}</span>
                <span class="history-date">{{ formatDate(file.date) }}</span>
              </div>
              <div v-if="file.preview" class="history-preview">{{ file.preview }}</div>
            </div>

            <div class="history-actions">
              <button @click.stop="deleteHistory(file.id)" class="delete-btn" title="删除">
                <span class="material-icon">&#xe872;</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isOpen: false,
      isLoading: false,
      historyFiles: [],
      selectedHistory: null,
      searchQuery: '',
      filterCharacter: '',
      historyPreviews: {}
    };
  },

  computed: {
    filteredHistoryFiles() {
      if (!this.searchQuery && !this.filterCharacter) {
        return this.historyFiles;
      }

      return this.historyFiles.filter(file => {
        const nameMatch = this.searchQuery
          ? (
              file.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
              (file.preview && file.preview.toLowerCase().includes(this.searchQuery.toLowerCase()))
            )
          : true;

        const characterMatch = this.filterCharacter
          ? (file.character && file.character.toLowerCase() === this.filterCharacter.toLowerCase())
          : true;

        return nameMatch && characterMatch;
      });
    },

    uniqueCharacters() {
      // 获取所有不重复的角色名称
      const characters = new Set();
      this.historyFiles.forEach(file => {
        if (file.character) {
          characters.add(file.character);
        }
      });
      return Array.from(characters).sort();
    }
  },

  mounted() {
    this.fetchHistoryFiles();
  },

  methods: {
    togglePanel() {
      this.isOpen = !this.isOpen;
    },

    fetchHistoryFiles() {
      this.isLoading = true;

      fetch('http://127.0.0.1:5000/list_history')
        .then(response => response.json())
        .then(data => {
          if (data.history) {
            this.historyFiles = data.history.map(file => ({
              id: file.id,
              name: file.name,
              date: new Date(file.date),
              character: this.extractCharacterName(file.name),
              preview: this.historyPreviews[file.id] || '',
              character_avatar: null // 将在后续步骤中填充
            }));

            // 获取聊天内容预览和角色头像
            this.historyFiles.forEach(file => {
              this.fetchHistoryPreview(file.id);
            });

            // 尝试获取角色头像
            this.loadAvatarsForHistory();
          }
          this.isLoading = false;
        })
        .catch(error => {
          console.error('Error fetching history files:', error);
          this.isLoading = false;
        });
    },

    loadAvatarsForHistory() {
      // 从父组件的设置中获取角色头像
      if (this.$parent && this.$parent.settings && this.$parent.settings.characterAvatars) {
        const characterAvatars = this.$parent.settings.characterAvatars;

        this.historyFiles.forEach((file, index) => {
          if (file.character) {
            // 找到对应的角色文件名，通常是 "角色名.txt"
            const characterFile = Object.keys(characterAvatars).find(key =>
              key.startsWith(file.character + '.') || key === file.character
            );

            if (characterFile && characterAvatars[characterFile]) {
              this.historyFiles[index].character_avatar = characterAvatars[characterFile];
            }
          }
        });
      }
    },

    fetchHistoryPreview(historyId) {
      // 获取聊天记录的预览内容
      fetch(`http://127.0.0.1:5000/get_history/${historyId}`)
        .then(response => response.json())
        .then(data => {
          if (data.success && data.history && data.history.messages) {
            const messages = data.history.messages;

            // 提取第一条用户消息作为预览
            const firstUserMessage = messages.find(msg => msg.type === 'user');

            if (firstUserMessage) {
              const preview = firstUserMessage.text.length > 60
                ? firstUserMessage.text.substring(0, 60) + '...'
                : firstUserMessage.text;

              // 更新历史文件的预览
              const index = this.historyFiles.findIndex(file => file.id === historyId);
              if (index !== -1) {
                this.$set(this.historyFiles[index], 'preview', preview);
              }

              // 存储预览以便下次使用
              this.historyPreviews[historyId] = preview;
            }

            // 如果有角色信息，更新角色
            if (data.history.character) {
              const characterName = data.history.character.split('.')[0];
              const index = this.historyFiles.findIndex(file => file.id === historyId);
              if (index !== -1) {
                this.$set(this.historyFiles[index], 'character', characterName);
              }
            }
          }
        })
        .catch(error => {
          console.error(`Error fetching preview for history ${historyId}:`, error);
        });
    },

    extractCharacterName(filename) {
      // 尝试从历史记录文件名中提取角色名称
      // 格式可能是 "2023-01-01_12-30-45_uuid.json" 或 "2023-01-01_12-30-45_角色名_uuid.json"
      const parts = filename.split('_');
      if (parts.length >= 3) {
        // 如果有额外的部分，可能包含角色名
        const lastPart = parts[parts.length - 1].split('.')[0];
        if (lastPart.length === 8 && /^[0-9a-f]+$/.test(lastPart)) {
          // 最后一部分是UUID，角色名可能在前面
          if (parts.length > 3) {
            return parts[2]; // 角色名可能在第三个位置
          }
        } else {
          // 最后一部分可能是角色名
          return lastPart;
        }
      }
      return ''; // 无法确定角色名
    },

    formatHistoryName(name) {
      // 提取文件名中的日期和主题
      const match = name.match(/(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})_(.+)\.json/);
      if (match) {
        const date = match[1];
        const time = match[2].replace(/-/g, ':');
        return `${date} ${time}`;
      }

      // 如果没有匹配到预期格式，提取日期部分
      const dateParts = name.split('_');
      if (dateParts.length >= 2) {
        const date = dateParts[0];
        const time = dateParts[1].replace(/-/g, ':');
        return `${date} ${time}`;
      }

      return name; // 如果没有匹配到任何格式，直接返回原名
    },

    formatDate(date) {
      // 检查是否是当天
      const today = new Date();
      const isToday = date.getDate() === today.getDate() &&
                      date.getMonth() === today.getMonth() &&
                      date.getFullYear() === today.getFullYear();

      // 检查是否是昨天
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      const isYesterday = date.getDate() === yesterday.getDate() &&
                          date.getMonth() === yesterday.getMonth() &&
                          date.getFullYear() === yesterday.getFullYear();

      if (isToday) {
        // 如果是当天，只显示时间
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `今天 ${hours}:${minutes}`;
      } else if (isYesterday) {
        // 如果是昨天，显示"昨天"和时间
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `昨天 ${hours}:${minutes}`;
      } else {
        // 其他情况，显示日期
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${month}-${day}`;
      }
    },

    selectHistory(historyId) {
      this.selectedHistory = historyId;
      this.$emit('select-history', historyId);

      // 在移动设备上，选择历史记录后自动关闭面板
      if (window.innerWidth <= 768) {
        this.isOpen = false;
      }
    },

    createNewChat() {
      this.$emit('create-new-chat');
      this.selectedHistory = null;

      // 在移动设备上，创建新聊天后自动关闭面板
      if (window.innerWidth <= 768) {
        this.isOpen = false;
      }
    },

    deleteHistory(historyId) {
      if (confirm('确定要删除这条聊天记录吗？此操作不可恢复。')) {
        fetch(`http://127.0.0.1:5000/delete_history/${historyId}`, {
          method: 'DELETE'
        })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              this.historyFiles = this.historyFiles.filter(file => file.id !== historyId);

              // 如果删除的是当前选中的历史记录，重置选择
              if (this.selectedHistory === historyId) {
                this.selectedHistory = null;
                this.$emit('select-history', null);
              }
            } else {
              alert('删除失败：' + data.error);
            }
          })
          .catch(error => {
            console.error('Error deleting history:', error);
            alert('删除失败，请检查服务器连接。');
          });
      }
    },

    getInitials(name) {
      if (!name) return '?';
      return name.charAt(0).toUpperCase();
    },

    clearFilters() {
      this.searchQuery = '';
      this.filterCharacter = '';
    }
  }
};
</script>

<style scoped>
/* Discord风格历史面板 */
.history-panel {
  position: fixed;
  top: 0;
  right: -320px;
  height: 100vh;
  width: 320px;
  background-color: #2f3136;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  z-index: 900;
  display: flex;
  color: #dcddde;
}

.history-panel.open {
  right: 0;
}

.history-toggle {
  position: absolute;
  left: -40px;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 60px;
  background-color: #202225;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.2);
  border-radius: 6px 0 0 6px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  color: #b9bbbe;
  transition: color 0.2s;
}

.history-toggle:hover {
  color: #ffffff;
}

.toggle-icon {
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.history-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #202225;
}

.history-header h3 {
  margin: 0;
  font-size: 16px;
  color: #ffffff;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.new-chat-btn {
  padding: 8px 12px;
  background-color: #5865f2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.2s;
}

.new-chat-btn:hover {
  background-color: #4752c4;
}

.history-filters {
  padding: 12px 16px;
  border-bottom: 1px solid #202225;
}

.search-box {
  position: relative;
  margin-bottom: 8px;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #72767d;
  font-size: 18px;
}

.clear-icon {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #72767d;
  font-size: 18px;
  cursor: pointer;
}

.clear-icon:hover {
  color: #dcddde;
}

.search-box input {
  width: 100%;
  padding: 8px 36px;
  background-color: #202225;
  border: none;
  border-radius: 4px;
  color: #dcddde;
  font-size: 14px;
  outline: none;
  transition: background-color 0.2s;
}

.search-box input:focus {
  background-color: #40444b;
}

.search-box input::placeholder {
  color: #72767d;
}

.filter-options {
  display: flex;
  gap: 8px;
}

.filter-select {
  width: 100%;
  padding: 6px 8px;
  background-color: #202225;
  border: 1px solid #40444b;
  border-radius: 4px;
  color: #dcddde;
  font-size: 13px;
  outline: none;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.history-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-item {
  padding: 12px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  transition: background-color 0.2s;
  position: relative;
}

.history-item:hover {
  background-color: #36393f;
}

.history-item.active {
  background-color: #36393f;
}

.history-item-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  flex-shrink: 0;
  overflow: hidden;
  background-color: #5865f2;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  color: white;
  font-size: 16px;
}

.avatar-image {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
}

.history-item-content {
  flex: 1;
  min-width: 0;
}

.history-title {
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 4px;
  font-size: 15px;
}

.history-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 12px;
  color: #b9bbbe;
}

.history-character {
  background-color: #40444b;
  padding: 2px 6px;
  border-radius: 10px;
}

.history-preview {
  font-size: 13px;
  color: #8e9297;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-actions {
  opacity: 0;
  transition: opacity 0.2s;
  position: absolute;
  right: 12px;
  top: 12px;
}

.history-item:hover .history-actions {
  opacity: 1;
}

.delete-btn {
  width: 28px;
  height: 28px;
  display: flex;
  justify-content: center;
  align-items: center;
  border: none;
  background-color: rgba(32, 34, 37, 0.5);
  color: #f04747;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-btn:hover {
  background-color: #f04747;
  color: white;
}

.loading-history,
.empty-history {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #8e9297;
  text-align: center;
  padding: 0 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #72767d;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #36393f;
  border-top: 3px solid #5865f2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.clear-filters-btn {
  margin-top: 12px;
  padding: 6px 12px;
  background-color: #4f545c;
  color: #dcddde;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.clear-filters-btn:hover {
  background-color: #5d6269;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式样式 */
@media (max-width: 768px) {
  .history-panel {
    width: 100%;
    right: -100%;
  }

  .history-toggle {
    left: -36px;
    width: 36px;
    height: 50px;
  }
}
</style>