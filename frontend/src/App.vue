<template>
  <div class="discord-app" :class="{ 'light-theme': settings.theme === 'light' }">
    <!-- 侧边栏 - 类似Discord服务器列表 -->
    <div class="sidebar">
      <!-- 角色图标列表 -->
      <div class="server-list">
        <div
          v-for="(character, index) in characterList"
          :key="index"
          @click="selectCharacter(character)"
          class="server-icon"
          :class="{ 'active': settings.selectedCharacter === character.file }"
          :title="character.name">
          <div class="server-icon-inner">
            <img v-if="character.avatar" :src="character.avatar" :alt="character.name" />
            <span v-else>{{ character.name.charAt(0) }}</span>
          </div>
        </div>

        <!-- 添加新角色按钮 -->
        <div class="server-icon add-server" @click="openSettings('character')" title="添加角色">
          <div class="server-icon-inner">
            <i class="fas fa-plus"></i>
          </div>
        </div>

        <!-- 设置按钮 -->
        <div class="server-icon settings-server" @click="openSettings('general')" title="设置">
          <div class="server-icon-inner">
            <i class="fas fa-cog"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-container" :style="backgroundStyle">
      <!-- 标题栏 -->
      <div class="header">
        <div class="header-info">
          <div class="header-icon" v-if="settings.selectedCharacter">
            <img v-if="getCurrentCharacterAvatar()" :src="getCurrentCharacterAvatar()" alt="角色头像">
            <span v-else>{{ getCharacterName(settings.selectedCharacter).charAt(0) }}</span>
          </div>
          <h2 v-if="settings.selectedCharacter">{{ getCharacterName(settings.selectedCharacter) }}</h2>
          <h2 v-else>选择一个角色开始聊天</h2>
        </div>

        <div class="header-actions">
          <button @click="toggleHistoryPanel" class="icon-button" title="历史记录">
            <i class="fas fa-history"></i>
          </button>
          <button @click="toggleTTS" class="icon-button" :class="{ 'active': ttsAvailable }" title="TTS语音">
            <i class="fas fa-volume-up"></i>
          </button>
          <div class="ai-model-badge" title="当前AI模型">
            <span>{{ currentModelLabel }}</span>
          </div>
        </div>
      </div>

      <!-- 聊天内容区 -->
      <div class="chat-content">
        <!-- 左侧消息区 -->
        <div class="messages-container" ref="messagesContainer">
          <div v-if="messages.length === 0" class="empty-chat">
            <div class="empty-chat-icon">
              <i class="fas fa-comments"></i>
            </div>
            <h3>开始一段新对话</h3>
            <p>选择一个角色并发送消息开始聊天</p>
          </div>

          <ChatMessage
            v-for="(msg, index) in messages"
            :key="index"
            :message="msg"
            :aiAvatar="getCurrentCharacterAvatar()"
            :userAvatar="settings.userAvatar"
          />
        </div>

        <!-- 右侧用户列表/信息面板 -->
        <div class="users-panel">
          <!-- 当前活动角色信息 -->
          <div v-if="settings.selectedCharacter" class="active-character">
            <div class="character-avatar">
              <img v-if="getCurrentCharacterAvatar()" :src="getCurrentCharacterAvatar()" alt="角色头像" />
              <div v-else class="default-avatar">{{ getCharacterName(settings.selectedCharacter).charAt(0) }}</div>
            </div>
            <div class="character-info">
              <h3>{{ getCharacterName(settings.selectedCharacter) }}</h3>
              <div class="status" :class="{ 'online': ttsAvailable }">
                <i :class="ttsAvailable ? 'fas fa-volume-up' : 'fas fa-volume-mute'"></i>
                {{ ttsAvailable ? '语音已启用' : '仅文字模式' }}
              </div>
            </div>
          </div>

          <!-- 角色描述 -->
          <div v-if="settings.selectedCharacter" class="character-description">
            <h4><i class="fas fa-info-circle"></i> 角色简介</h4>
            <p>{{ getCharacterDescription() }}</p>
          </div>

          <!-- AI模型信息 -->
          <div class="ai-model-info">
            <h4><i class="fas fa-robot"></i> 当前AI模型</h4>
            <div class="model-section">
              <div class="model-provider">
                <i :class="getProviderIcon()"></i>
                {{ getProviderName() }}
              </div>
              <div class="model-badge">{{ getCurrentModelInfo() }}</div>
            </div>
            <div class="model-settings">
              <div class="model-setting">
                <span>温度: {{ getModelTemperature() }}</span>
                <div class="temperature-bar" :style="{ '--value': getModelTemperature() * 100 + '%' }"></div>
              </div>
            </div>
          </div>

          <!-- 预设信息 -->
          <div class="preset-info" v-if="currentPreset">
            <h4><i class="fas fa-sliders-h"></i> 当前预设</h4>
            <div class="preset-name">{{ currentPreset.name }}</div>
            <div class="preset-tags">
              <span v-for="(tag, index) in currentPreset.tags" :key="index" class="preset-tag">
                <i class="fas fa-tag"></i> {{ tag }}
              </span>
            </div>
          </div>

          <!-- 系统状态 -->
          <div class="system-status">
            <h4><i class="fas fa-server"></i> 系统状态</h4>
            <div class="status-items">
              <div class="status-item">
                <i class="fas fa-plug" :class="{ 'text-success': backendConnected, 'text-danger': !backendConnected }"></i>
                <span>后端API: {{ backendConnected ? '已连接' : '未连接' }}</span>
              </div>
              <div class="status-item">
                <i class="fas fa-volume-up" :class="{ 'text-success': ttsAvailable, 'text-danger': !ttsAvailable }"></i>
                <span>TTS服务: {{ ttsAvailable ? '已连接' : '未连接' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-container">
        <button
          @click="toggleListening"
          :disabled="isWaitingForResponse || !settings.selectedCharacter"
          class="action-button mic-button"
          :class="{ 'listening': isListening }"
          title="语音输入">
          <i :class="isListening ? 'fas fa-stop' : 'fas fa-microphone'"></i>
        </button>

        <div class="text-input-wrapper">
          <textarea
            ref="messageInput"
            v-model="newMessage"
            @keydown.enter.prevent="sendMessage"
            placeholder="输入消息..."
            :disabled="isWaitingForResponse || !settings.selectedCharacter"
            rows="1"
            @input="autoResizeTextarea"></textarea>

          <div v-if="isListening && interimTranscript" class="interim-transcript">
            {{ interimTranscript }}
          </div>
        </div>

        <button
          @click="sendMessage"
          class="action-button send-button"
          :disabled="isWaitingForResponse || !newMessage.trim() || !settings.selectedCharacter"
          title="发送消息">
          <i class="fas fa-paper-plane"></i>
        </button>
      </div>
    </div>

    <!-- 设置面板 -->
    <Settings
      :show="showSettings"
      :characterFiles="characterFiles"
      :initialSettings="settings"
      :initialTab="activeSettingsTab"
      @close="closeSettings"
      @update-settings="updateSettings"
      @refresh-characters="fetchCharacterFiles"
    />

    <!-- 历史记录面板 -->
    <HistoryPanel
      ref="historyPanel"
      @select-history="loadHistory"
      @create-new-chat="createNewChat"
    />

    <!-- 通知Toast -->
    <div class="toast-container">
      <div v-for="(toast, index) in toasts" :key="index"
        class="toast"
        :class="{ 'show': toast.show, 'toast-success': toast.type === 'success', 'toast-error': toast.type === 'error', 'toast-info': toast.type === 'info' }">
        <i :class="getToastIcon(toast)"></i>
        <span>{{ toast.message }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import ChatMessage from './components/ChatMessage.vue';
import Settings from './components/SettingsPanel.vue';
import HistoryPanel from './components/HistoryPanel.vue';

export default {
  components: {
    ChatMessage,
    Settings,
    HistoryPanel
  },

  data() {
    return {
      messages: [],
      newMessage: '',
      recognition: null,
      isListening: false,
      characterFiles: [],
      characterList: [], // 角色列表（带有名称和头像）
      firstMessage: true,
      isWaitingForResponse: false,
      lastSpeechTimestamp: 0,
      silenceTimer: null,
      interimTranscript: '',
      showSettings: false,
      activeSettingsTab: 'general',
      currentChatId: null,
      ttsAvailable: false,
      ttsRetryCount: 0, // TTS重试计数
      currentPreset: null, // 当前使用的预设
      backendConnected: false, // 后端连接状态
      toasts: [], // 通知列表
      settings: {
        aiAvatar: null,
        userAvatar: null,
        chatBackground: null,
        selectedCharacter: null,
        currentAIProvider: 'gemini',
        theme: 'dark',
        characterAvatars: {}, // 存储角色和头像的映射
        characterDescriptions: {}, // 存储角色描述
        selectedPreset: null, // 选择的预设名称
        tts: {
          speed: 1.0,
          autoPlay: true,
          refAudio: null
        },
        gemini: {
          apiKey: "",
          model: "gemini-2.0-flash-lite-preview-02-05",
          temperature: 0.7
        },
        openai: {
          apiKey: "",
          model: "gpt-4o",
          temperature: 0.7
        },
        claude: {
          apiKey: "",
          model: "claude-3-5-sonnet-20240229",
          temperature: 0.7
        }
      }
    };
  },

  computed: {
    backgroundStyle() {
      if (this.settings.chatBackground) {
        return {
          backgroundImage: `url(${this.settings.chatBackground})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        };
      }
      return {};
    },

    currentModelLabel() {
      // 返回当前AI提供商的简写名称
      const provider = this.settings.currentAIProvider;
      if (provider === 'gemini') return 'Gemini';
      if (provider === 'openai') return 'GPT';
      if (provider === 'claude') return 'Claude';
      return 'AI';
    }
  },

  mounted() {
    this.fetchCharacterFiles();
    this.loadSettings();
    this.setupSpeechRecognition();
    this.checkTTSAvailability();
    this.setupMessageInputAutoResize();
    this.checkBackendConnection();
    this.loadCurrentPreset();

    // 添加事件监听器以在调整窗口大小时更新文本区域高度
    window.addEventListener('resize', this.autoResizeTextarea);

    // 添加Font Awesome
    this.loadFontAwesome();
  },

  beforeUnmount() {
    // 移除事件监听器
    window.removeEventListener('resize', this.autoResizeTextarea);
  },

  methods: {
    loadFontAwesome() {
      // 动态加载Font Awesome
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
      document.head.appendChild(link);
    },

    setupMessageInputAutoResize() {
      if (this.$refs.messageInput) {
        this.autoResizeTextarea();
      }
    },

    autoResizeTextarea() {
      const textarea = this.$refs.messageInput;
      if (!textarea) return;

      // 重置高度
      textarea.style.height = 'auto';

      // 计算新高度（最大4行）
      const newHeight = Math.min(textarea.scrollHeight, 96); // 24px × 4 = 96px
      textarea.style.height = `${newHeight}px`;
    },

    getCurrentModelInfo() {
      const provider = this.settings.currentAIProvider;
      const model = this.settings[provider]?.model || '未知模型';

      // 将模型ID转换为更友好的名称
      const modelNames = {
        // Gemini
        'gemini-2.0-flash-lite-preview-02-05': 'Gemini 2.0 Flash Lite',
        'gemini-2.0-pro': 'Gemini 2.0 Pro',
        'gemini-2.0-pro-vision': 'Gemini 2.0 Pro Vision',
        'gemini-pro': 'Gemini 1.0 Pro',
        'gemini-pro-vision': 'Gemini 1.0 Pro Vision',
        'gemini-1.5-pro': 'Gemini 1.5 Pro',
        'gemini-1.5-flash': 'Gemini 1.5 Flash',

        // OpenAI
        'gpt-3.5-turbo': 'GPT-3.5 Turbo',
        'gpt-4': 'GPT-4',
        'gpt-4-turbo': 'GPT-4 Turbo',
        'gpt-4o': 'GPT-4o',
        'gpt-4o-mini': 'GPT-4o Mini',
        'gpt-4-vision': 'GPT-4 Vision',
        'gpt-3.5-turbo-16k': 'GPT-3.5 Turbo 16K',

        // Claude
        'claude-3-5-sonnet-20240229': 'Claude 3.5 Sonnet',
        'claude-3-opus-20240229': 'Claude 3 Opus',
        'claude-3-sonnet-20240229': 'Claude 3 Sonnet',
        'claude-3-haiku-20240307': 'Claude 3 Haiku',
        'claude-2.0': 'Claude 2',
        'claude-2.1': 'Claude 2.1'
      };

      return modelNames[model] || model;
    },

    getProviderName() {
      const provider = this.settings.currentAIProvider;

      if (provider === 'gemini') return 'Google Gemini';
      if (provider === 'openai') return 'OpenAI';
      if (provider === 'claude') return 'Anthropic Claude';

      return '未知提供商';
    },

    getProviderIcon() {
      const provider = this.settings.currentAIProvider;

      if (provider === 'gemini') return 'fab fa-google';
      if (provider === 'openai') return 'fas fa-brain';
      if (provider === 'claude') return 'fas fa-star';

      return 'fas fa-robot';
    },

    getModelTemperature() {
      const provider = this.settings.currentAIProvider;
      return this.settings[provider]?.temperature || 0.7;
    },

    selectCharacter(character) {
      if (character && character.file) {
        this.settings.selectedCharacter = character.file;
        this.createNewChat(); // 选择新角色后开始新聊天
        this.saveSettings();
      }
    },

    getCharacterName(characterFile) {
      if (!characterFile) return "选择角色";
      return characterFile.split('.')[0];
    },

    getCharacterDescription() {
      const selectedCharacter = this.settings.selectedCharacter;
      if (!selectedCharacter) return "";

      return this.settings.characterDescriptions[selectedCharacter] ||
          "暂无角色描述。您可以在设置中添加角色描述。";
    },

    getCurrentCharacterAvatar() {
      const selectedCharacter = this.settings.selectedCharacter;
      if (!selectedCharacter) return null;

      return this.settings.characterAvatars[selectedCharacter] || null;
    },

    checkTTSAvailability() {
      // 默认尝试启用TTS
      this.ttsAvailable = false;
      this.ttsRetryCount = 0;
      this.tryConnectTTS();
    },

    tryConnectTTS() {
      // 尝试连接TTS服务
      fetch('http://127.0.0.1:7865/sdapi/v1/server-info')
          .then(response => {
            if (response.ok) {
              this.ttsAvailable = true;
              console.log('TTS服务可用');
              this.showToast('TTS服务已连接', 'success');
            } else {
              this.handleTTSConnectionFailure();
            }
          })
          .catch(error => {
            console.warn('TTS连接错误:', error);
            this.handleTTSConnectionFailure();
          });
    },

    handleTTSConnectionFailure() {
      this.ttsRetryCount++;
      if (this.ttsRetryCount < 2) {
        console.log(`TTS连接失败，正在尝试第${this.ttsRetryCount + 1}次连接...`);
        // 3秒后重试
        setTimeout(() => this.tryConnectTTS(), 3000);
      } else {
        console.log('TTS服务不可用，将使用纯文本模式');
        this.ttsAvailable = false;
      }
    },

    toggleTTS() {
      if (this.ttsAvailable) {
        this.ttsAvailable = false;
        this.showToast('已关闭TTS语音', 'info');
      } else {
        this.checkTTSAvailability();
      }
    },

    checkBackendConnection() {
      fetch('http://127.0.0.1:5000/health')
          .then(response => {
            this.backendConnected = response.ok;
            if (response.ok) {
              console.log('后端API已连接');
            } else {
              console.warn('后端API返回错误状态码');
              this.showToast('无法连接到后端服务', 'error');
            }
          })
          .catch(error => {
            console.error('后端API连接错误:', error);
            this.backendConnected = false;
            this.showToast('无法连接到后端服务', 'error');
          });
    },

    loadCurrentPreset() {
      if (!this.settings.selectedPreset) return;

      fetch(`http://127.0.0.1:5000/get_preset/${this.settings.selectedPreset}`)
          .then(response => response.json())
          .then(data => {
            if (data.success && data.preset) {
              this.currentPreset = data.preset;
            }
          })
          .catch(error => console.error('Error loading preset:', error));
    },

    setupSpeechRecognition() {
      if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        this.recognition.lang = 'zh-CN';
        this.recognition.continuous = true;
        this.recognition.interimResults = true;

        this.recognition.onresult = (event) => {
          if (this.isWaitingForResponse) return;

          let finalTranscript = '';
          this.interimTranscript = '';
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
              this.lastSpeechTimestamp = Date.now();
            } else {
              this.interimTranscript += event.results[i][0].transcript;
            }
          }

          if (finalTranscript) {
            this.newMessage = finalTranscript;
            this.resetSilenceTimer();
            this.autoResizeTextarea();
          } else if (this.interimTranscript) {
            this.newMessage = this.interimTranscript;
            this.autoResizeTextarea();
          }
        };

        this.recognition.onend = () => {
          if (this.isListening) {
            this.recognition.start();
          }
        };

        this.recognition.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          this.isListening = false;
          this.isWaitingForResponse = false;

          if (event.error === 'no-speech') {
            this.showToast('没有检测到声音，请说话', 'info');
          } else if (event.error === 'audio-capture') {
            this.showToast('无法访问麦克风，请检查麦克风是否已连接', 'error');
          } else if (event.error === 'not-allowed') {
            this.showToast('未授权麦克风访问，请在浏览器设置中允许此网站使用麦克风', 'error');
          } else {
            this.showToast('语音识别出错: ' + event.error, 'error');
          }
        };
      } else {
        this.showToast('您的浏览器不支持语音识别', 'error');
      }
    },

    fetchCharacterFiles() {
      fetch('http://127.0.0.1:5000/list_characters')
          .then(response => response.json())
          .then(data => {
            if (data.characters) {
              this.characterFiles = data.characters;
              // 处理角色列表
              this.characterList = data.characters.map(file => {
                const name = file.split('.')[0];
                return {
                  file: file,
                  name: name,
                  avatar: this.settings.characterAvatars?.[file] || null
                };
              });
            }
          })
          .catch(error => {
            console.error('Error fetching characters:', error);
            this.showToast('获取角色列表失败', 'error');
          });
    },

    loadSettings() {
      fetch('http://127.0.0.1:5000/get_settings')
          .then(response => response.json())
          .then(data => {
            if (data.settings) {
              // 合并设置，保留默认值
              this.settings = {
                ...this.settings,
                ...data.settings,
                gemini: {...this.settings.gemini, ...data.settings.gemini},
                openai: {...this.settings.openai, ...data.settings.openai},
                claude: {...this.settings.claude, ...data.settings.claude},
                tts: {...this.settings.tts, ...data.settings.tts}
              };

              // 更新角色列表中的头像
              this.updateCharacterList();

              // 加载当前预设
              this.loadCurrentPreset();
            }
          })
          .catch(error => console.error('Error loading settings:', error));
    },

    updateCharacterList() {
      // 更新角色列表中的头像
      this.characterList = this.characterFiles.map(file => {
        const name = file.split('.')[0];
        return {
          file: file,
          name: name,
          avatar: this.settings.characterAvatars?.[file] || null
        };
      });
    },

    updateSettings(newSettings) {
      this.settings = {...this.settings, ...newSettings};
      this.saveSettings();
      this.updateCharacterList();

      // 如果预设发生变化，重新加载预设
      if (newSettings.selectedPreset !== this.settings.selectedPreset) {
        this.loadCurrentPreset();
      }

      this.closeSettings();
    },

    saveSettings() {
      // 保存设置到服务器
      fetch('http://127.0.0.1:5000/save_settings', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(this.settings),
      })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              console.log('设置已保存');
            } else {
              console.error('Error saving settings:', data.error);
              this.showToast('保存设置失败', 'error');
            }
          })
          .catch(error => console.error('Error saving settings:', error));
    },

    async sendMessage() {
      if (!this.newMessage.trim() || this.isWaitingForResponse) return;

      if (!this.settings.selectedCharacter) {
        this.showToast('请先选择一个角色', 'info');
        this.openSettings('character');
        return;
      }

      const messageText = this.newMessage.trim();
      this.messages.push({text: messageText, type: 'user', timestamp: new Date()});
      this.newMessage = '';
      this.interimTranscript = '';
      this.isWaitingForResponse = true;
      this.autoResizeTextarea();

      // 添加一个带加载指示器的AI消息
      const aiMessageIndex = this.messages.push({
        text: '',
        type: 'ai',
        loading: true,
        timestamp: new Date()
      }) - 1;

      // 准备请求参数
      let requestData = {
        message: messageText,
        character: this.settings.selectedCharacter,
        first_message: this.firstMessage,
        current_chat_id: this.currentChatId,
        ai_provider: this.settings.currentAIProvider,
        ai_settings: this.settings[this.settings.currentAIProvider],
        tts_enabled: this.ttsAvailable,
        tts_settings: this.settings.tts,
        preset: this.settings.selectedPreset
      };

      try {
        const response = await fetch('http://127.0.0.1:5000/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(requestData),
        });

        const data = await response.json();

        if (data.response) {
          this.messages[aiMessageIndex].text = data.response;
          this.messages[aiMessageIndex].loading = false;
          this.messages[aiMessageIndex].tts_played = data.tts_played;

          if (data.chat_id) {
            this.currentChatId = data.chat_id;
          }
        } else {
          this.messages[aiMessageIndex].text = 'Error: ' + (data.error || 'Unknown error');
          this.messages[aiMessageIndex].loading = false;
          this.showToast('AI回复生成失败', 'error');
        }

        this.scrollToBottom();
        this.firstMessage = false;

      } catch (error) {
        console.error('Error:', error);
        this.messages[aiMessageIndex].text = 'Error: Could not connect to the server.';
        this.messages[aiMessageIndex].loading = false;
        this.scrollToBottom();
        this.showToast('无法连接到服务器', 'error');
      } finally {
        this.isWaitingForResponse = false;
        this.resetSilenceTimer();
      }
    },

    toggleListening() {
      if (this.isListening) {
        this.stopListening();
      } else {
        this.startListening();
      }
    },

    startListening() {
      if (!this.recognition) return;
      this.isListening = true;
      this.recognition.start();
      this.resetSilenceTimer();
      this.showToast('语音识别已开启', 'info');
    },

    stopListening() {
      this.isListening = false;
      if (this.recognition) {
        this.recognition.stop();
      }
      clearTimeout(this.silenceTimer);

      // 如果有内容并且停止录音，可以自动发送消息
      if (this.newMessage.trim() && !this.isWaitingForResponse) {
        setTimeout(() => this.sendMessage(), 300);
      }
    },

    resetSilenceTimer() {
      clearTimeout(this.silenceTimer);
      this.silenceTimer = setTimeout(() => {
        if (this.newMessage.trim() && !this.isWaitingForResponse && this.isListening) {
          this.sendMessage();
        }
      }, 2000);
    },

    scrollToBottom() {
      this.$nextTick(() => {
        if (this.$refs.messagesContainer) {
          this.$refs.messagesContainer.scrollTop = this.$refs.messagesContainer.scrollHeight;
        }
      });
    },

    openSettings(tab = 'general') {
      this.activeSettingsTab = tab;
      this.showSettings = true;
    },

    closeSettings() {
      this.showSettings = false;
    },

    toggleHistoryPanel() {
      if (this.$refs.historyPanel) {
        this.$refs.historyPanel.togglePanel();
      }
    },

    loadHistory(historyId) {
      if (!historyId) {
        this.createNewChat();
        return;
      }

      fetch(`http://127.0.0.1:5000/get_history/${historyId}`)
          .then(response => response.json())
          .then(data => {
            if (data.history) {
              this.messages = data.history.messages || [];
              this.currentChatId = historyId;
              this.firstMessage = false;

              if (data.history.character) {
                this.settings.selectedCharacter = data.history.character;
              }

              this.scrollToBottom();
            }
          })
          .catch(error => {
            console.error('Error loading history:', error);
            this.showToast('加载聊天记录失败', 'error');
          });
    },

    createNewChat() {
      this.messages = [];
      this.currentChatId = null;
      this.firstMessage = true;
    },

    showToast(message, type = 'info') {
      const toast = {
        id: Date.now(),
        message,
        type,
        show: true
      };

      this.toasts.push(toast);

      // 3秒后自动隐藏
      setTimeout(() => {
        const index = this.toasts.findIndex(t => t.id === toast.id);
        if (index !== -1) {
          this.toasts[index].show = false;

          // 动画结束后移除
          setTimeout(() => {
            this.toasts = this.toasts.filter(t => t.id !== toast.id);
          }, 300);
        }
      }, 3000);
    },

    getToastIcon(toast) {
      if (toast.type === 'success') return 'fas fa-check-circle';
      if (toast.type === 'error') return 'fas fa-exclamation-circle';
      if (toast.type === 'info') return 'fas fa-info-circle';
      return 'fas fa-bell';
    }
  }
};
</script>

<style>
/* 引入Font Awesome (通过CDN) */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Whitney', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  overflow: hidden;
}

/* Discord风格应用 */
.discord-app {
  width: 100vw;
  height: 100vh;
  display: flex;
  background-color: #36393f;
  color: #dcddde;
  font-family: 'Whitney', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  overflow: hidden;
}

/* 浅色主题 */
.discord-app.light-theme {
  background-color: #ffffff;
  color: #2e3338;
}

.light-theme .sidebar {
  background-color: #e3e5e8;
}

.light-theme .server-icon {
  background-color: #ffffff;
  color: #6a7480;
}

.light-theme .header {
  background-color: #ffffff;
  border-bottom-color: #ebedef;
}

.light-theme .header h2 {
  color: #060607;
}

.light-theme .icon-button {
  color: #4f5660;
}

.light-theme .messages-container {
  background-color: #ffffff;
  border-right-color: #ebedef;
}

.light-theme .users-panel {
  background-color: #f2f3f5;
}

.light-theme .input-container {
  background-color: #ffffff;
  border-top-color: #ebedef;
}

.light-theme .text-input-wrapper {
  background-color: #f6f6f7;
}

.light-theme .text-input-wrapper textarea {
  color: #2e3338;
}

.light-theme .action-button {
  color: #4f5660;
}

/* 侧边栏 - 类似Discord服务器列表 */
.sidebar {
  width: 72px;
  height: 100%;
  background-color: #202225;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 0;
  overflow-y: auto;
  z-index: 10;
}

.server-list {
  display: flex;
  flex-direction: column;
  width: 100%;
  align-items: center;
  gap: 10px;
}

.server-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #36393f;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 18px;
  font-weight: bold;
  position: relative;
}

.server-icon-inner {
  width: 100%;
  height: 100%;
  border-radius: inherit;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.server-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.server-icon:hover {
  border-radius: 16px;
  background-color: #5865f2;
  color: white;
}

.server-icon.active {
  border-radius: 16px;
  background-color: #5865f2;
  color: white;
}

.server-icon.active::before {
  content: '';
  position: absolute;
  left: -15px;
  width: 8px;
  height: 40px;
  border-radius: 0 4px 4px 0;
  background-color: white;
}

.add-server {
  background-color: #36393f;
  color: #3ba55c;
  font-size: 22px;
}

.add-server:hover {
  background-color: #3ba55c;
  color: white;
}

.settings-server {
  background-color: #36393f;
  color: #b9bbbe;
  font-size: 22px;
  margin-top: auto;
}

.settings-server:hover {
  background-color: #b9bbbe;
  color: #202225;
}

/* 主内容区 */
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background-color: #36393f;
  position: relative;
}

.light-theme .main-container {
  background-color: #ffffff;
}

/* 标题栏 */
.header {
  height: 48px;
  padding: 0 16px;
  border-bottom: 1px solid #2f3136;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #36393f;
  z-index: 10;
}

.light-theme .header {
  border-bottom-color: #ebedef;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #5865f2;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 14px;
  font-weight: bold;
  color: white;
  overflow: hidden;
}

.header-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.light-theme .header h2 {
  color: #060607;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.icon-button {
  background: none;
  border: none;
  color: #b9bbbe;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 16px;
}

.light-theme .icon-button {
  color: #4f5660;
}

.icon-button:hover {
  background-color: rgba(79, 84, 92, 0.32);
  color: white;
}

.light-theme .icon-button:hover {
  background-color: rgba(116, 127, 141, 0.24);
  color: #060607;
}

.icon-button.active {
  color: #3ba55c;
}

.ai-model-badge {
  background-color: #5865f2;
  color: white;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 聊天内容区 */
.chat-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 空聊天状态 */
.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #8e9297;
  text-align: center;
  padding: 0 20px;
}

.empty-chat-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #72767d;
}

.empty-chat h3 {
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 8px;
}

.light-theme .empty-chat h3 {
  color: #060607;
}

.empty-chat p {
  font-size: 14px;
  color: #8e9297;
}

/* 左侧消息区 */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  scroll-behavior: smooth;
  background-color: #36393f;
  border-right: 1px solid #2f3136;
}

.light-theme .messages-container {
  background-color: #ffffff;
  border-right-color: #ebedef;
}

/* 右侧用户列表/信息面板 */
.users-panel {
  width: 240px;
  background-color: #2f3136;
  padding: 16px;
  overflow-y: auto;
  flex-shrink: 0;
}

.light-theme .users-panel {
  background-color: #f2f3f5;
}

.active-character {
  display: flex;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid #40444b;
  margin-bottom: 16px;
}

.light-theme .active-character {
  border-bottom-color: #e3e5e8;
}

.character-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 12px;
  background-color: #5865f2;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  color: white;
}

.character-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.character-info h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.light-theme .character-info h3 {
  color: #060607;
}

.status {
  font-size: 12px;
  color: #b9bbbe;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status.online {
  color: #3ba55c;
}

.character-description,
.ai-model-info,
.preset-info,
.system-status {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #40444b;
}

.light-theme .character-description,
.light-theme .ai-model-info,
.light-theme .preset-info,
.light-theme .system-status {
  border-bottom-color: #e3e5e8;
}

.character-description h4,
.ai-model-info h4,
.preset-info h4,
.system-status h4 {
  margin: 0 0 8px 0;
  font-size: 12px;
  text-transform: uppercase;
  color: #b9bbbe;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
}

.light-theme .character-description h4,
.light-theme .ai-model-info h4,
.light-theme .preset-info h4,
.light-theme .system-status h4 {
  color: #6a7480;
}

.character-description p {
  font-size: 14px;
  color: #dcddde;
  line-height: 1.4;
  margin: 0;
}

.light-theme .character-description p {
  color: #2e3338;
}

.model-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 8px;
}

.model-provider {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #dcddde;
}

.light-theme .model-provider {
  color: #2e3338;
}

.model-badge {
  background-color: #4f545c;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  display: inline-block;
}

.model-settings {
  margin-top: 10px;
}

.model-setting {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
  font-size: 12px;
  color: #b9bbbe;
}

.light-theme .model-setting {
  color: #6a7480;
}

.temperature-bar {
  height: 6px;
  width: 100%;
  background: #40444b;
  border-radius: 3px;
  position: relative;
}

.light-theme .temperature-bar {
  background: #e3e5e8;
}

.temperature-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: var(--value, 0%);
  background: linear-gradient(to right, #3ba55c, #5865f2);
  border-radius: 3px;
}

.preset-name {
  font-size: 14px;
  color: #dcddde;
  font-weight: 500;
  margin-bottom: 6px;
}

.light-theme .preset-name {
  color: #2e3338;
}

.preset-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.preset-tag {
  font-size: 11px;
  padding: 2px 6px;
  background-color: #40444b;
  border-radius: 10px;
  color: #b9bbbe;
  display: flex;
  align-items: center;
  gap: 4px;
}

.light-theme .preset-tag {
  background-color: #e3e5e8;
  color: #6a7480;
}

.status-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #dcddde;
}

.light-theme .status-item {
  color: #2e3338;
}

.text-success {
  color: #3ba55c;
}

.text-danger {
  color: #f04747;
}

/* 输入区域 */
.input-container {
  padding: 16px;
  background-color: #36393f;
  border-top: 1px solid #2f3136;
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.light-theme .input-container {
  background-color: #ffffff;
  border-top-color: #ebedef;
}

.text-input-wrapper {
  flex: 1;
  background-color: #40444b;
  border-radius: 8px;
  padding: 10px 16px;
  min-height: 24px;
  max-height: 144px; /* 最多6行 */
  overflow-y: auto;
  position: relative;
}

.light-theme .text-input-wrapper {
  background-color: #f6f6f7;
}

.text-input-wrapper textarea {
  width: 100%;
  border: none;
  background: transparent;
  outline: none;
  color: #dcddde;
  font-size: 14px;
  line-height: 1.4;
  resize: none;
  padding: 0;
  font-family: inherit;
}

.light-theme .text-input-wrapper textarea {
  color: #2e3338;
}

.text-input-wrapper textarea::placeholder {
  color: #72767d;
}

.interim-transcript {
  position: absolute;
  bottom: -20px;
  left: 0;
  right: 0;
  font-size: 12px;
  color: #b9bbbe;
  background-color: rgba(32, 34, 37, 0.9);
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.light-theme .interim-transcript {
  background-color: rgba(227, 229, 232, 0.9);
  color: #2e3338;
}

.action-button {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background-color: transparent;
  border: none;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
  color: #b9bbbe;
  font-size: 18px;
}

.light-theme .action-button {
  color: #4f5660;
}

.action-button:hover {
  background-color: #4f545c;
  color: white;
}

.light-theme .action-button:hover {
  background-color: #e3e5e8;
  color: #060607;
}

.action-button:disabled {
  color: #4f545c;
  cursor: not-allowed;
}

.light-theme .action-button:disabled {
  color: #c7ccd1;
}

.mic-button.listening {
  color: #f04747;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(240, 71, 71, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(240, 71, 71, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(240, 71, 71, 0);
  }
}

.send-button {
  color: #3ba55c;
}

.send-button:hover {
  background-color: #3ba55c;
  color: white;
}

/* 通知Toast */
.toast-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1001;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 320px;
}

.toast {
  padding: 12px 16px;
  background-color: #2f3136;
  color: #dcddde;
  border-radius: 4px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 10px;
  transform: translateX(100%);
  opacity: 0;
  transition: all 0.3s ease;
}

.light-theme .toast {
  background-color: #ffffff;
  color: #2e3338;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.toast.show {
  transform: translateX(0);
  opacity: 1;
}

.toast-success {
  border-left: 4px solid #3ba55c;
}

.toast-error {
  border-left: 4px solid #f04747;
}

.toast-info {
  border-left: 4px solid #5865f2;
}

.toast i {
  font-size: 18px;
}

.toast-success i {
  color: #3ba55c;
}

.toast-error i {
  color: #f04747;
}

.toast-info i {
  color: #5865f2;
}

/* 响应式样式 */
@media (max-width: 1200px) {
  .users-panel {
    width: 200px;
  }
}

@media (max-width: 992px) {
  .users-panel {
    display: none;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 60px;
  }

  .server-icon {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }

  .server-icon.active::before {
    height: 32px;
  }
}

@media (max-width: 576px) {
  .discord-app {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    height: 60px;
    flex-direction: row;
    padding: 0 10px;
  }

  .server-list {
    flex-direction: row;
    height: 100%;
  }

  .server-icon {
    width: 36px;
    height: 36px;
    font-size: 14px;
  }

  .server-icon.active::before {
    display: none;
  }
}
</style>