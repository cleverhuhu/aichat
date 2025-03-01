<template>
  <div class="settings-overlay" v-if="show" @click.self="closeSettings">
    <div class="settings-container">
      <div class="settings-header">
        <h2>
          <i class="fas fa-cog"></i>
          设置
        </h2>
        <button class="close-button" @click="closeSettings">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="settings-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="{ active: activeTab === tab.id }"
          :title="tab.name">
          <i :class="tab.icon"></i>
          <span class="tab-name">{{ tab.name }}</span>
        </button>
      </div>

      <div class="settings-content">
        <!-- 基本设置 -->
        <div v-if="activeTab === 'general'" class="settings-section">
          <h3><i class="fas fa-palette"></i> 外观设置</h3>

          <!-- 头像设置 -->
          <div class="setting-item">
            <div class="setting-label">用户头像</div>
            <div class="avatar-picker">
              <div class="current-avatar" :style="{ 'background-image': `url(${settings.userAvatar || '/default-user-avatar.png'})` }"></div>
              <input type="file" ref="userAvatarUpload" @change="handleAvatarUpload('user')" accept="image/*" style="display: none">
              <button @click="triggerFileUpload('user')" class="upload-button">
                <i class="fas fa-upload"></i> 上传图片
              </button>
            </div>
          </div>

          <!-- 背景设置 -->
          <div class="setting-item">
            <div class="setting-label">聊天背景</div>
            <div class="background-picker">
              <div class="background-preview" :style="{ 'background-image': `url(${settings.chatBackground || '/default-background.png'})` }"></div>
              <input type="file" ref="backgroundUpload" @change="handleBackgroundUpload" accept="image/*" style="display: none">
              <button @click="triggerBackgroundUpload" class="upload-button">
                <i class="fas fa-upload"></i> 上传图片
              </button>
            </div>
          </div>

          <!-- 主题设置 -->
          <div class="setting-item">
            <div class="setting-label">界面主题</div>
            <div class="theme-options">
              <button
                class="theme-option"
                :class="{ active: settings.theme === 'dark' }"
                @click="settings.theme = 'dark'">
                <i class="fas fa-moon"></i> 暗色主题
              </button>
              <button
                class="theme-option"
                :class="{ active: settings.theme === 'light' }"
                @click="settings.theme = 'light'">
                <i class="fas fa-sun"></i> 亮色主题
              </button>
            </div>
          </div>
        </div>

        <!-- 角色设置 -->
        <div v-if="activeTab === 'character'" class="settings-section">
          <h3><i class="fas fa-users"></i> 角色管理</h3>

          <!-- 角色列表 -->
          <div class="character-grid">
            <div
              v-for="charFile in characterFiles"
              :key="charFile"
              class="character-card"
              :class="{ 'selected': settings.selectedCharacter === charFile }"
              @click="selectCharacter(charFile)">

              <div class="character-avatar">
                <img v-if="getCharacterAvatar(charFile)" :src="getCharacterAvatar(charFile)" alt="角色头像">
                <div v-else class="default-avatar">{{ charFile.split('.')[0].charAt(0) }}</div>
              </div>

              <div class="character-name">
                {{ charFile.split('.')[0] }}
              </div>

              <div class="character-actions">
                <button @click.stop="editCharacter(charFile)" class="action-button" title="编辑角色">
                  <i class="fas fa-edit"></i>
                </button>
              </div>
            </div>

            <!-- 添加新角色 -->
            <div class="character-card add-character" @click="showAddCharacterModal = true">
              <div class="add-icon">
                <i class="fas fa-plus"></i>
              </div>
              <div>添加角色</div>
            </div>
          </div>

          <!-- 当前选择的角色设置 -->
          <div v-if="settings.selectedCharacter" class="character-settings">
            <h4><i class="fas fa-id-card"></i> 角色详情</h4>

            <div class="setting-item">
              <div class="setting-label">角色头像</div>
              <div class="avatar-picker">
                <div class="current-avatar" :style="{ 'background-image': `url(${getCharacterAvatar(settings.selectedCharacter) || '/default-character-avatar.png'})` }"></div>
                <input type="file" ref="characterAvatarUpload" @change="handleCharacterAvatarUpload" accept="image/*" style="display: none">
                <button @click="triggerCharacterAvatarUpload" class="upload-button">
                  <i class="fas fa-upload"></i> 上传头像
                </button>
              </div>
            </div>

            <div class="setting-item">
              <div class="setting-label">角色描述</div>
              <textarea
                v-model="characterDescription"
                placeholder="添加角色描述..."
                class="character-description-input"
                @input="updateCharacterDescription"></textarea>
            </div>
          </div>
        </div>

        <!-- AI预设设置（类似SillyTavern） -->
        <div v-if="activeTab === 'presets'" class="settings-section">
          <h3><i class="fas fa-sliders-h"></i> AI预设管理</h3>

          <div class="presets-container">
            <!-- 预设选择器 -->
            <div class="presets-sidebar">
              <div class="preset-search">
                <i class="fas fa-search search-icon"></i>
                <input
                  type="text"
                  v-model="presetSearch"
                  placeholder="搜索预设..."
                  class="preset-search-input">
                <i v-if="presetSearch" @click="presetSearch = ''" class="fas fa-times clear-icon"></i>
              </div>

              <div class="preset-list">
                <div
                  v-for="(preset, index) in filteredPresets"
                  :key="index"
                  @click="selectPreset(preset)"
                  class="preset-item"
                  :class="{ active: selectedPreset && selectedPreset.name === preset.name }">
                  <div class="preset-icon">
                    <i class="fas fa-file-alt"></i>
                  </div>
                  <div class="preset-info">
                    <div class="preset-name">{{ preset.name }}</div>
                    <div class="preset-tags">
                      <span
                        v-for="(tag, tagIndex) in preset.tags.slice(0, 2)"
                        :key="tagIndex"
                        class="preset-tag">
                        <i class="fas fa-tag"></i> {{ tag }}
                      </span>
                      <span v-if="preset.tags.length > 2" class="preset-tag-more">+{{ preset.tags.length - 2 }}</span>
                    </div>
                  </div>
                </div>

                <div class="preset-item add-preset" @click="createNewPreset">
                  <div class="preset-icon">
                    <i class="fas fa-plus"></i>
                  </div>
                  <div class="preset-name">创建新预设</div>
                </div>
              </div>
            </div>

            <!-- 预设编辑区 -->
            <div class="preset-editor">
              <div v-if="selectedPreset" class="preset-editor-content">
                <div class="preset-header">
                  <div class="setting-item">
                    <div class="setting-label">预设名称</div>
                    <input type="text" v-model="selectedPreset.name" class="preset-name-input">
                  </div>

                  <div class="preset-actions">
                    <button @click="saveCurrentPreset" class="save-preset-button">
                      <i class="fas fa-save"></i> 保存预设
                    </button>
                    <button @click="deleteCurrentPreset" class="delete-preset-button">
                      <i class="fas fa-trash"></i> 删除预设
                    </button>
                  </div>
                </div>

                <div class="setting-item">
                  <div class="setting-label">标签</div>
                  <div class="tags-input">
                    <div v-for="(tag, index) in selectedPreset.tags" :key="index" class="tag-item">
                      {{ tag }}
                      <span @click="removePresetTag(index)" class="tag-remove">×</span>
                    </div>
                    <input
                      type="text"
                      v-model="newTagInput"
                      @keydown.enter="addPresetTag"
                      placeholder="添加标签..."
                      class="tag-input">
                  </div>
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <div class="label-with-actions">
                      <span>预设内容</span>
                      <button @click="addNewInstruction" class="add-instruction-button">
                        <i class="fas fa-plus"></i> 添加提示词
                      </button>
                    </div>
                  </div>

                  <div class="preset-instructions">
                    <div v-for="(instruction, index) in selectedPreset.instructions" :key="index" class="instruction-item">
                      <div class="instruction-header">
                        <div class="instruction-title">{{ instruction.title || `提示词 ${index + 1}` }}</div>
                        <div class="instruction-controls">
                          <label class="switch" title="启用/禁用此提示词">
                            <input type="checkbox" v-model="instruction.enabled">
                            <span class="slider"></span>
                          </label>
                          <button @click="removeInstruction(index)" class="instruction-remove" title="删除此提示词">
                            <i class="fas fa-trash"></i>
                          </button>
                          <button @click="instruction.expanded = !instruction.expanded" class="instruction-expand" title="展开/折叠">
                            <i :class="instruction.expanded ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                          </button>
                        </div>
                      </div>

                      <div v-if="instruction.expanded" class="instruction-content">
                        <div class="instruction-field">
                          <div class="field-label">标题</div>
                          <input type="text" v-model="instruction.title" placeholder="提示词标题">
                        </div>

                        <div class="instruction-field">
                          <div class="field-label">角色</div>
                          <select v-model="instruction.role">
                            <option value="system">系统 (System)</option>
                            <option value="user">用户 (User)</option>
                            <option value="assistant">助手 (Assistant)</option>
                          </select>
                        </div>

                        <div class="instruction-field">
                          <div class="field-label">内容</div>
                          <textarea
                            v-model="instruction.content"
                            placeholder="输入提示词内容..."
                            class="instruction-textarea"></textarea>
                        </div>

                        <div class="instruction-field">
                          <div class="field-label">注入位置</div>
                          <select v-model="instruction.injection_position">
                            <option value="0">开始</option>
                            <option value="1">中间</option>
                            <option value="2">结束</option>
                          </select>
                        </div>

                        <div class="instruction-field">
                          <div class="field-label">注入深度</div>
                          <input type="number" v-model="instruction.injection_depth" min="0" max="10">
                        </div>

                        <div class="instruction-field checkbox-field">
                          <label class="checkbox-label">
                            <input type="checkbox" v-model="instruction.system_prompt">
                            <span>系统提示词</span>
                          </label>
                        </div>

                        <div class="instruction-field checkbox-field">
                          <label class="checkbox-label">
                            <input type="checkbox" v-model="instruction.marker">
                            <span>标记</span>
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="preset-order-section">
                  <div class="setting-label">提示词顺序</div>
                  <div class="preset-order-list">
                    <draggable
                      v-model="selectedPreset.prompt_order"
                      handle=".drag-handle"
                      animation="150"
                      ghost-class="ghost"
                      @end="updatePromptOrder">
                      <div
                        v-for="(promptItem, ) in selectedPreset.prompt_order"
                        :key="promptItem.identifier"
                        class="prompt-order-item">
                        <span class="drag-handle">
                          <i class="fas fa-grip-lines"></i>
                        </span>
                        <span class="prompt-order-name">
                          {{ getPromptNameByIdentifier(promptItem.identifier) || promptItem.identifier }}
                        </span>
                        <label class="switch">
                          <input type="checkbox" v-model="promptItem.enabled">
                          <span class="slider"></span>
                        </label>
                      </div>
                    </draggable>
                  </div>
                </div>

                <div class="advanced-settings">
                  <div class="setting-label">高级设置</div>

                  <div class="setting-item">
                    <div class="setting-label">温度</div>
                    <div class="slider-container">
                      <input type="range" v-model="selectedPreset.temperature" min="0" max="2" step="0.05" class="temperature-slider">
                      <div class="slider-value">{{ selectedPreset.temperature }}</div>
                    </div>
                  </div>

                  <div class="setting-item">
                    <div class="setting-label">Top P</div>
                    <div class="slider-container">
                      <input type="range" v-model="selectedPreset.top_p" min="0" max="1" step="0.05" class="temperature-slider">
                      <div class="slider-value">{{ selectedPreset.top_p }}</div>
                    </div>
                  </div>

                  <div class="setting-item">
                    <div class="setting-label">Top K</div>
                    <div class="slider-container">
                      <input type="range" v-model="selectedPreset.top_k" min="0" max="100" step="1" class="temperature-slider">
                      <div class="slider-value">{{ selectedPreset.top_k }}</div>
                    </div>
                  </div>

                  <div class="setting-item">
                    <div class="setting-label">Presence Penalty</div>
                    <div class="slider-container">
                      <input type="range" v-model="selectedPreset.presence_penalty" min="0" max="2" step="0.1" class="temperature-slider">
                      <div class="slider-value">{{ selectedPreset.presence_penalty }}</div>
                    </div>
                  </div>

                  <div class="setting-item">
                    <div class="setting-label">Frequency Penalty</div>
                    <div class="slider-container">
                      <input type="range" v-model="selectedPreset.frequency_penalty" min="0" max="2" step="0.1" class="temperature-slider">
                      <div class="slider-value">{{ selectedPreset.frequency_penalty }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else class="no-preset-selected">
                <div class="no-preset-icon">
                  <i class="fas fa-file-alt fa-4x"></i>
                </div>
                <div class="no-preset-text">选择或创建一个预设</div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI模型设置 -->
        <div v-if="activeTab === 'models'" class="settings-section">
          <h3><i class="fas fa-robot"></i> AI模型设置</h3>

          <div class="setting-item">
            <div class="setting-label">当前使用的AI模型</div>
            <select v-model="settings.currentAIProvider" class="provider-select">
              <option value="gemini">Google Gemini</option>
              <option value="openai">OpenAI GPT</option>
              <option value="claude">Anthropic Claude</option>
            </select>
          </div>

          <!-- Gemini 设置 -->
          <div v-if="settings.currentAIProvider === 'gemini'" class="api-settings">
            <h4><i class="fas fa-code"></i> Google Gemini 设置</h4>
            <div class="setting-item">
              <div class="setting-label">API Key</div>
              <div class="api-key-input-group">
                <input
                  :type="showApiKey.gemini ? 'text' : 'password'"
                  v-model="settings.gemini.apiKey"
                  placeholder="输入Gemini API Key"
                  class="api-key-input">
                <button
                  @click="showApiKey.gemini = !showApiKey.gemini"
                  class="show-key-button"
                  :title="showApiKey.gemini ? '隐藏API Key' : '显示API Key'">
                  <i :class="showApiKey.gemini ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
            </div>
            <div class="setting-item">
              <div class="setting-label">模型</div>
              <select v-model="settings.gemini.model" class="model-select">
                <optgroup label="Gemini 2.0">
                  <option value="gemini-2.0-pro-exp-02-05">Gemini 2.0 Pro</option>

                  <option value="gemini-2.0-flash-lite-preview-02-05">Gemini 2.0 Flash Lite</option>
                </optgroup>
                <optgroup label="Gemini 1.5">
                  <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                  <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                </optgroup>
                <optgroup label="Gemini 1.0">
                  <option value="gemini-pro">Gemini 1.0 Pro</option>
                  <option value="gemini-pro-vision">Gemini 1.0 Pro Vision</option>
                </optgroup>
              </select>
            </div>
            <div class="setting-item">
              <div class="setting-label">温度 ({{ settings.gemini.temperature }})</div>
              <div class="slider-container">
                <input type="range" v-model="settings.gemini.temperature" min="0" max="1" step="0.1" class="temperature-slider">
                <div class="slider-labels">
                  <span>精确</span>
                  <span>平衡</span>
                  <span>创意</span>
                </div>
              </div>
            </div>
          </div>

          <!-- OpenAI设置 -->
          <div v-if="settings.currentAIProvider === 'openai'" class="api-settings">
            <h4><i class="fas fa-brain"></i> OpenAI 设置</h4>
            <div class="setting-item">
              <div class="setting-label">API Key</div>
              <div class="api-key-input-group">
                <input
                  :type="showApiKey.openai ? 'text' : 'password'"
                  v-model="settings.openai.apiKey"
                  placeholder="输入OpenAI API Key"
                  class="api-key-input">
                <button
                  @click="showApiKey.openai = !showApiKey.openai"
                  class="show-key-button"
                  :title="showApiKey.openai ? '隐藏API Key' : '显示API Key'">
                  <i :class="showApiKey.openai ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
            </div>
            <div class="setting-item">
              <div class="setting-label">模型</div>
              <select v-model="settings.openai.model" class="model-select">
                <optgroup label="GPT-4">
                  <option value="gpt-4o">GPT-4o (最新)</option>
                  <option value="gpt-4o-mini">GPT-4o Mini</option>
                  <option value="gpt-4-turbo">GPT-4 Turbo</option>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-4-vision">GPT-4 Vision</option>
                </optgroup>
                <optgroup label="GPT-3.5">
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="gpt-3.5-turbo-16k">GPT-3.5 Turbo 16K</option>
                </optgroup>
              </select>
            </div>
            <div class="setting-item">
              <div class="setting-label">温度 ({{ settings.openai.temperature }})</div>
              <div class="slider-container">
                <input type="range" v-model="settings.openai.temperature" min="0" max="1" step="0.1" class="temperature-slider">
                <div class="slider-labels">
                  <span>精确</span>
                  <span>平衡</span>
                  <span>创意</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Claude设置 -->
          <div v-if="settings.currentAIProvider === 'claude'" class="api-settings">
            <h4><i class="fas fa-star"></i> Anthropic Claude 设置</h4>
            <div class="setting-item">
              <div class="setting-label">API Key</div>
              <div class="api-key-input-group">
                <input
                  :type="showApiKey.claude ? 'text' : 'password'"
                  v-model="settings.claude.apiKey"
                  placeholder="输入Claude API Key"
                  class="api-key-input">
                <button
                  @click="showApiKey.claude = !showApiKey.claude"
                  class="show-key-button"
                  :title="showApiKey.claude ? '隐藏API Key' : '显示API Key'">
                  <i :class="showApiKey.claude ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
            </div>
            <div class="setting-item">
              <div class="setting-label">模型</div>
              <select v-model="settings.claude.model" class="model-select">
                <optgroup label="Claude 3.7">
                  <option value="claude-3-7-sonnet-20250219">Claude 3.7 Sonnet </option>
                </optgroup>
                <optgroup label="Claude 3.5">
                  <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet </option>
                </optgroup>
                <optgroup label="Claude 3">
                  <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                  <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
                  <option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
                </optgroup>
                <optgroup label="Claude 2">
                  <option value="claude-2.0">Claude 2</option>
                  <option value="claude-2.1">Claude 2.1</option>
                </optgroup>
              </select>
            </div>
            <div class="setting-item">
              <div class="setting-label">温度 ({{ settings.claude.temperature }})</div>
              <div class="slider-container">
                <input type="range" v-model="settings.claude.temperature" min="0" max="1" step="0.1" class="temperature-slider">
                <div class="slider-labels">
                  <span>精确</span>
                  <span>平衡</span>
                  <span>创意</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- TTS设置 -->
        <div v-if="activeTab === 'tts'" class="settings-section">
          <h3><i class="fas fa-volume-up"></i> TTS语音设置</h3>

          <div class="tts-status">
            <div class="status-indicator" :class="{ 'online': ttsAvailable, 'offline': !ttsAvailable }">
              <i :class="ttsAvailable ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
              {{ ttsAvailable ? 'TTS服务已连接' : 'TTS服务未连接' }}
            </div>
            <button @click="checkTTSConnection" class="check-connection-button">
              <i class="fas fa-sync-alt"></i>
              检查连接
            </button>
          </div>

          <div class="setting-item">
            <div class="setting-label">TTS服务URL</div>
            <div class="url-input-group">
              <input type="text" v-model="ttsUrl" placeholder="http://localhost:7865" class="tts-url-input">
              <button @click="saveTTSUrl" class="save-url-button">
                <i class="fas fa-save"></i> 保存
              </button>
            </div>
          </div>

          <div v-if="ttsAvailable" class="tts-settings">
            <div class="setting-item">
              <div class="setting-label">语音速度</div>
              <div class="slider-container">
                <input type="range" v-model="settings.tts.speed" min="0.5" max="2" step="0.1" class="tts-slider">
                <div class="slider-value">{{ settings.tts.speed }}x</div>
              </div>
            </div>

            <div class="setting-item">
              <div class="setting-label">播放设置</div>
              <div class="checkbox-option">
                <label class="switch">
                  <input type="checkbox" v-model="settings.tts.autoPlay">
                  <span class="slider"></span>
                </label>
                <span>自动播放TTS</span>
              </div>
            </div>

            <div class="setting-item">
              <div class="setting-label">参考音频</div>
              <div class="ref-audio-controls">
                <input type="file" ref="refAudioUpload" @change="handleRefAudioUpload" accept="audio/*" style="display: none">
                <button @click="triggerRefAudioUpload" class="upload-button">
                  <i class="fas fa-upload"></i> 上传参考音频
                </button>
                <div v-if="settings.tts.refAudio" class="ref-audio-file">
                  <i class="fas fa-file-audio"></i> {{ getRefAudioName() }}
                  <button @click="playRefAudio" class="play-button" title="播放">
                    <i class="fas fa-play"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="settings-footer">
        <button @click="closeSettings" class="cancel-button">
          <i class="fas fa-times"></i> 取消
        </button>
        <button @click="saveSettings" class="save-button">
          <i class="fas fa-save"></i> 保存设置
        </button>
      </div>
    </div>

    <!-- 添加角色模态框 -->
    <div v-if="showAddCharacterModal" class="modal-overlay" @click.self="showAddCharacterModal = false">
      <div class="modal-container">
        <div class="modal-header">
          <h3><i class="fas fa-user-plus"></i> 添加新角色</h3>
          <button @click="showAddCharacterModal = false" class="close-button">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-content">
          <div class="setting-item">
            <div class="setting-label">角色名称</div>
            <input type="text" v-model="newCharacterName" placeholder="输入角色名称" class="input-field">
          </div>

          <div class="setting-item">
            <div class="setting-label">角色描述</div>
            <textarea v-model="newCharacterDescription" placeholder="输入角色描述..." class="textarea-field"></textarea>
          </div>

          <div class="setting-item">
            <div class="setting-label">角色头像</div>
            <div class="avatar-picker">
              <div class="current-avatar" :style="{ 'background-image': `url(${newCharacterAvatar || '/default-character-avatar.png'})` }"></div>
              <input type="file" ref="newCharacterAvatarUpload" @change="handleNewCharacterAvatarUpload" accept="image/*" style="display: none">
              <button @click="triggerNewCharacterAvatarUpload" class="upload-button">
                <i class="fas fa-upload"></i> 上传头像
              </button>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="showAddCharacterModal = false" class="cancel-button">
            <i class="fas fa-times"></i> 取消
          </button>
          <button @click="createNewCharacter" class="confirm-button">
            <i class="fas fa-check"></i> 创建角色
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SettingsPanel',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    characterFiles: {
      type: Array,
      default: () => []
    },
    initialSettings: {
      type: Object,
      default: () => ({})
    },
    initialTab: {
      type: String,
      default: 'general'
    }
  },

  data() {
    return {
      activeTab: 'general',
      tabs: [
        { id: 'general', name: '基本设置', icon: 'fas fa-cog' },
        { id: 'character', name: '角色设置', icon: 'fas fa-users' },
        { id: 'presets', name: 'AI预设', icon: 'fas fa-sliders-h' },
        { id: 'models', name: 'AI模型', icon: 'fas fa-robot' },
        { id: 'tts', name: '语音设置', icon: 'fas fa-volume-up' }
      ],
      settings: {
        aiAvatar: null,
        userAvatar: null,
        chatBackground: null,
        selectedCharacter: null,
        theme: 'dark',
        characterAvatars: {}, // 存储角色头像
        characterDescriptions: {}, // 存储角色描述
        currentAIProvider: 'gemini',
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
      },
      showApiKey: {
        gemini: false,
        openai: false,
        claude: false
      },
      characterDescription: '', // 当前选中角色的描述
      ttsAvailable: false,
      ttsUrl: 'http://localhost:7865',

      // AI预设相关
      presets: [],
      selectedPreset: null,
      presetSearch: '',
      newTagInput: '',

      // 添加角色相关
      showAddCharacterModal: false,
      newCharacterName: '',
      newCharacterDescription: '',
      newCharacterAvatar: null
    };
  },

  computed: {
    filteredPresets() {
      if (!this.presetSearch) return this.presets;

      const search = this.presetSearch.toLowerCase();
      return this.presets.filter(preset => {
        return preset.name.toLowerCase().includes(search) ||
               (preset.tags && preset.tags.some(tag => tag.toLowerCase().includes(search)));
      });
    }
  },

  created() {
    // 加载初始设置
    if (this.initialSettings && Object.keys(this.initialSettings).length > 0) {
      // 深度合并设置
      this.settings = this.mergeSettings(this.settings, this.initialSettings);
    }

    // 设置初始选中的标签页
    if (this.initialTab) {
      this.activeTab = this.initialTab;
    }

    // 加载预设
    this.fetchPresets();

    // 检查TTS可用性
    this.checkTTSConnection();
  },

  watch: {
    'settings.selectedCharacter': {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.characterDescription = this.settings.characterDescriptions[newVal] || '';
        } else {
          this.characterDescription = '';
        }
      }
    },
    initialTab(newVal) {
      this.activeTab = newVal;
    }
  },

  methods: {
    mergeSettings(target, source) {
      // 创建一个深拷贝
      const result = JSON.parse(JSON.stringify(target));

      // 遍历source的所有属性
      for (const key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          // 如果是对象并且两边都有这个属性，递归合并
          if (typeof source[key] === 'object' && source[key] !== null &&
              typeof result[key] === 'object' && result[key] !== null) {
            result[key] = this.mergeSettings(result[key], source[key]);
          } else {
            // 否则直接赋值
            result[key] = source[key];
          }
        }
      }

      return result;
    },

    fetchPresets() {
      fetch('http://127.0.0.1:5000/list_presets')
        .then(response => response.json())
        .then(data => {
          if (data.success && data.presets) {
            // 加载预设列表
            const loadPromises = data.presets.map(presetName => {
              return fetch(`http://127.0.0.1:5000/get_preset/${presetName}`)
                .then(res => res.json())
                .then(presetData => {
                  if (presetData.success && presetData.preset) {
                    return presetData.preset;
                  }
                  return null;
                });
            });

            Promise.all(loadPromises).then(loadedPresets => {
              // 过滤掉加载失败的预设
              const validPresets = loadedPresets.filter(preset => preset !== null);

              // 为每个预设添加默认属性
              validPresets.forEach(preset => {
                // 确保每个指令都有expanded属性
                if (preset.instructions) {
                  preset.instructions.forEach(instruction => {
                    instruction.expanded = false;
                  });
                }

                // 如果没有标签，添加空数组
                if (!preset.tags) {
                  preset.tags = [];
                }

                // 如果没有提示词顺序，添加空数组
                if (!preset.prompt_order) {
                  preset.prompt_order = [];
                }
              });

              this.presets = validPresets;

              // 如果没有预设，添加默认预设
              if (this.presets.length === 0) {
                this.addDefaultPresets();
              }
            });
          } else {
            // 如果没有预设，添加默认预设
            this.addDefaultPresets();
          }
        })
        .catch(error => {
          console.error('Error fetching presets:', error);
          this.addDefaultPresets();
        });
    },

    addDefaultPresets() {
      // 创建默认预设
      const defaultPresets = [
        {
          name: '通用对话',
          tags: ['基础', '对话'],
          temperature: 0.7,
          top_p: 0.95,
          top_k: 40,
          presence_penalty: 0,
          frequency_penalty: 0,
          instructions: [
            {
              title: '角色设定',
              content: '你是一个友好的AI助手，请保持对话礼貌和专业。',
              position: 'start',
              role: 'system',
              injection_position: 0,
              injection_depth: 4,
              system_prompt: true,
              marker: false,
              enabled: true,
              expanded: false
            }
          ],
          prompt_order: [
            {
              identifier: 'main',
              enabled: true
            },
            {
              identifier: 'charDescription',
              enabled: true
            }
          ]
        },
        {
          name: '小说创作',
          tags: ['创意', '写作', '小说'],
          temperature: 1.0,
          top_p: 0.95,
          top_k: 40,
          presence_penalty: 0.5,
          frequency_penalty: 0.5,
          instructions: [
            {
              title: '写作风格',
              content: '以详细生动的方式描述场景和人物，使用丰富的形容词和比喻。',
              position: 'start',
              role: 'system',
              injection_position: 0,
              injection_depth: 4,
              system_prompt: true,
              marker: false,
              enabled: true,
              expanded: false
            },
            {
              title: '对话格式',
              content: '使用引号表示对话，用括号表示动作和表情。',
              position: 'before_ai',
              role: 'system',
              injection_position: 0,
              injection_depth: 4,
              system_prompt: true,
              marker: false,
              enabled: true,
              expanded: false
            }
          ],
          prompt_order: [
            {
              identifier: 'main',
              enabled: true
            },
            {
              identifier: 'charDescription',
              enabled: true
            }
          ]
        }
      ];

      this.presets = defaultPresets;
    },

    checkTTSConnection() {
      this.ttsAvailable = false;

      // 使用保存的URL或默认URL
      const url = this.ttsUrl || 'http://localhost:7865';

      fetch(`${url}/sdapi/v1/server-info`)
        .then(response => {
          this.ttsAvailable = response.ok;
        })
        .catch(error => {
          console.warn('TTS连接错误:', error);
          this.ttsAvailable = false;
        });
    },

    saveTTSUrl() {
      // 保存TTS URL到设置
      if (this.ttsUrl) {
        this.settings.ttsUrl = this.ttsUrl;
        this.checkTTSConnection();
      }
    },

    closeSettings() {
      this.$emit('close');
    },

    triggerFileUpload(type) {
      if (type === 'user') {
        this.$refs.userAvatarUpload.click();
      }
    },

    triggerCharacterAvatarUpload() {
      this.$refs.characterAvatarUpload.click();
    },

    triggerNewCharacterAvatarUpload() {
      this.$refs.newCharacterAvatarUpload.click();
    },

    triggerRefAudioUpload() {
      this.$refs.refAudioUpload.click();
    },

    triggerBackgroundUpload() {
      this.$refs.backgroundUpload.click();
    },

    handleAvatarUpload(type) {
      const fileInput = type === 'user'
        ? this.$refs.userAvatarUpload
        : this.$refs.aiAvatarUpload;

      const file = fileInput.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        // 根据类型设置不同的头像
        if (type === 'user') {
          this.settings.userAvatar = e.target.result;
        } else if (type === 'ai') {
          this.settings.aiAvatar = e.target.result;
        }
      };
      reader.readAsDataURL(file);
    },

    handleCharacterAvatarUpload() {
      const file = this.$refs.characterAvatarUpload.files[0];
      if (!file || !this.settings.selectedCharacter) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        if (!this.settings.characterAvatars) {
          this.settings.characterAvatars = {};
        }
        this.settings.characterAvatars[this.settings.selectedCharacter] = e.target.result;
      };
      reader.readAsDataURL(file);
    },

    handleNewCharacterAvatarUpload() {
      const file = this.$refs.newCharacterAvatarUpload.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        this.newCharacterAvatar = e.target.result;
      };
      reader.readAsDataURL(file);
    },

    handleRefAudioUpload() {
      const file = this.$refs.refAudioUpload.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        this.settings.tts.refAudio = {
          name: file.name,
          data: e.target.result
        };
      };
      reader.readAsDataURL(file);
    },

    handleBackgroundUpload() {
      const file = this.$refs.backgroundUpload.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        this.settings.chatBackground = e.target.result;
      };
      reader.readAsDataURL(file);
    },

    selectCharacter(charFile) {
      this.settings.selectedCharacter = charFile;
      this.characterDescription = this.settings.characterDescriptions[charFile] || '';
    },

    updateCharacterDescription() {
      if (!this.settings.selectedCharacter) return;

      if (!this.settings.characterDescriptions) {
        this.settings.characterDescriptions = {};
      }

      this.settings.characterDescriptions[this.settings.selectedCharacter] = this.characterDescription;
    },

    getCharacterAvatar(characterFile) {
      return this.settings.characterAvatars?.[characterFile] || null;
    },

    editCharacter(charFile) {
      // 编辑角色，可以在这里实现编辑角色的功能
      this.selectCharacter(charFile);
    },

    createNewCharacter() {
      if (!this.newCharacterName.trim()) {
        alert('请输入角色名称');
        return;
      }

      // 创建角色文件
      const characterData = {
        name: this.newCharacterName,
        description: this.newCharacterDescription,
        file_name: `${this.newCharacterName}.txt`
      };

      fetch('http://127.0.0.1:5000/create_character', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(characterData)
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // 保存头像
          if (this.newCharacterAvatar) {
            if (!this.settings.characterAvatars) {
              this.settings.characterAvatars = {};
            }
            this.settings.characterAvatars[data.file_name] = this.newCharacterAvatar;
          }

          // 保存描述
          if (this.newCharacterDescription) {
            if (!this.settings.characterDescriptions) {
              this.settings.characterDescriptions = {};
            }
            this.settings.characterDescriptions[data.file_name] = this.newCharacterDescription;
          }

          // 更新角色列表
          this.$emit('refresh-characters');

          // 选中新创建的角色
          this.settings.selectedCharacter = data.file_name;

          // 重置表单
          this.newCharacterName = '';
          this.newCharacterDescription = '';
          this.newCharacterAvatar = null;
          this.showAddCharacterModal = false;
        } else {
          alert('创建角色失败: ' + data.error);
        }
      })
      .catch(error => {
        console.error('Error creating character:', error);
        alert('创建角色失败，请检查服务器连接');
      });
    },

    selectPreset(preset) {
      this.selectedPreset = JSON.parse(JSON.stringify(preset)); // 深拷贝

      // 确保每个指令都有expanded属性
      if (this.selectedPreset.instructions) {
        this.selectedPreset.instructions.forEach(instruction => {
          if (instruction.expanded === undefined) {
            instruction.expanded = false;
          }
        });
      }
    },

    createNewPreset() {
      const newPreset = {
        name: '新预设',
        tags: ['自定义'],
        temperature: 0.7,
        top_p: 0.95,
        top_k: 40,
        presence_penalty: 0,
        frequency_penalty: 0,
        instructions: [
          {
            title: '基本指令',
            content: '请按照以下方式回答...',
            role: 'system',
            injection_position: 0,
            injection_depth: 4,
            system_prompt: true,
            marker: false,
            enabled: true,
            expanded: true
          }
        ],
        prompt_order: [
          {
            identifier: 'main',
            enabled: true
          },
          {
            identifier: 'charDescription',
            enabled: true
          }
        ]
      };

      this.presets.push(newPreset);
      this.selectPreset(newPreset);
    },

    addPresetTag() {
      if (!this.newTagInput.trim() || !this.selectedPreset) return;

      if (!this.selectedPreset.tags) {
        this.selectedPreset.tags = [];
      }

      if (!this.selectedPreset.tags.includes(this.newTagInput.trim())) {
        this.selectedPreset.tags.push(this.newTagInput.trim());
      }

      this.newTagInput = '';
    },

    removePresetTag(index) {
      if (!this.selectedPreset || !this.selectedPreset.tags) return;

      this.selectedPreset.tags.splice(index, 1);
    },

    addNewInstruction() {
      if (!this.selectedPreset) return;

      if (!this.selectedPreset.instructions) {
        this.selectedPreset.instructions = [];
      }

      this.selectedPreset.instructions.push({
        title: '',
        content: '',
        role: 'system',
        injection_position: 0,
        injection_depth: 4,
        system_prompt: true,
        marker: false,
        enabled: true,
        expanded: true
      });
    },

    removeInstruction(index) {
      if (!this.selectedPreset || !this.selectedPreset.instructions) return;

      this.selectedPreset.instructions.splice(index, 1);
    },

    updatePromptOrder() {
      // 更新提示词顺序后的处理
      console.log("Prompt order updated");
    },

    getPromptNameByIdentifier(identifier) {
      // 获取预设中指令名称
      if (!this.selectedPreset || !this.selectedPreset.instructions) return identifier;

      const instruction = this.selectedPreset.instructions.find(inst => inst.identifier === identifier);
      if (instruction) {
        return instruction.title || identifier;
      }

      // 一些系统默认的标识符
      const defaultNames = {
        'main': '主要提示词',
        'charDescription': '角色描述',
        'charPersonality': '角色性格',
        'worldInfoBefore': '世界设定(前)',
        'worldInfoAfter': '世界设定(后)',
        'chatHistory': '聊天历史',
        'dialogueExamples': '对话示例',
        'scenario': '场景'
      };

      return defaultNames[identifier] || identifier;
    },

    saveCurrentPreset() {
      if (!this.selectedPreset) return;

      // 更新内存中的预设
      const index = this.presets.findIndex(p => p.name === this.selectedPreset.name);
      if (index !== -1) {
        this.presets[index] = JSON.parse(JSON.stringify(this.selectedPreset));
      } else {
        this.presets.push(JSON.parse(JSON.stringify(this.selectedPreset)));
      }

      // 保存到服务器
      fetch('http://127.0.0.1:5000/save_preset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.selectedPreset)
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          alert('预设保存成功');
        } else {
          alert('预设保存失败: ' + data.error);
        }
      })
      .catch(error => {
        console.error('Error saving preset:', error);
        alert('预设保存失败，请检查服务器连接');
      });
    },

    deleteCurrentPreset() {
      if (!this.selectedPreset || !confirm('确定要删除这个预设吗？此操作不可恢复。')) return;

      // 从内存中删除
      const index = this.presets.findIndex(p => p.name === this.selectedPreset.name);
      if (index !== -1) {
        this.presets.splice(index, 1);
      }

      // 从服务器删除
      fetch(`http://127.0.0.1:5000/delete_preset/${encodeURIComponent(this.selectedPreset.name)}`, {
        method: 'DELETE'
      })
      .catch(error => console.error('Error deleting preset:', error));

      // 清除选中的预设
      this.selectedPreset = null;
    },

    getRefAudioName() {
      if (!this.settings.tts.refAudio) return '';

      const name = this.settings.tts.refAudio.name;
      if (name.length > 20) {
        return name.substring(0, 17) + '...';
      }
      return name;
    },

    playRefAudio() {
      if (!this.settings.tts.refAudio) return;

      const audio = new Audio(this.settings.tts.refAudio.data);
      audio.play();
    },

    saveSettings() {
      this.$emit('update-settings', JSON.parse(JSON.stringify(this.settings)));
    }
  }
};
</script>

<style scoped>
/* 引入Font Awesome (通过CDN) */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

/* Discord风格样式 */
.settings-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.settings-container {
  width: 850px;
  max-width: 95%;
  height: 80vh;
  background-color: #36393f;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  color: #dcddde;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #2f3136;
  background-color: #2f3136;
}

.settings-header h2 {
  margin: 0;
  font-size: 18px;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 10px;
}

.close-button {
  background: none;
  border: none;
  color: #b9bbbe;
  cursor: pointer;
  transition: color 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 32px;
  height: 32px;
  border-radius: 4px;
}

.close-button:hover {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.1);
}

.settings-tabs {
  display: flex;
  padding: 8px 16px;
  background-color: #2f3136;
  overflow-x: auto;
  border-bottom: 1px solid #202225;
}

.settings-tabs button {
  padding: 10px 16px;
  border: none;
  background: none;
  cursor: pointer;
  color: #b9bbbe;
  font-weight: 500;
  font-size: 14px;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.settings-tabs button.active {
  color: #fff;
  background-color: #3f4249;
}

.settings-tabs button:hover:not(.active) {
  background-color: #3f4249;
}

.tab-name {
  margin-left: 4px;
}

.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #36393f;
}

.settings-section {
  margin-bottom: 24px;
}

h3 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  padding-bottom: 8px;
  border-bottom: 1px solid #40444b;
  display: flex;
  align-items: center;
  gap: 8px;
}

h4 {
  margin-top: 16px;
  margin-bottom: 12px;
  color: #b9bbbe;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.setting-item {
  margin-bottom: 16px;
}

.setting-label {
  font-size: 12px;
  color: #b9bbbe;
  margin-bottom: 8px;
  font-weight: 600;
}

.label-with-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

input[type="text"],
input[type="password"],
input[type="number"],
select,
textarea {
  width: 100%;
  padding: 10px 12px;
  border: none;
  background-color: #40444b;
  color: #dcddde;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  transition: box-shadow 0.2s;
}

input[type="text"]:focus,
input[type="password"]:focus,
input[type="number"]:focus,
select:focus,
textarea:focus {
  box-shadow: 0 0 0 2px #5865f2;
}

.textarea-field {
  resize: vertical;
  min-height: 80px;
}

.character-description-input {
  resize: vertical;
  min-height: 100px;
  margin-bottom: 16px;
}

.avatar-picker,
.background-picker {
  display: flex;
  align-items: center;
  gap: 12px;
}

.current-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #40444b;
  background-size: cover;
  background-position: center;
  border: 3px solid #36393f;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.background-preview {
  width: 120px;
  height: 67px;
  border-radius: 4px;
  background-color: #40444b;
  background-size: cover;
  background-position: center;
  border: 2px solid #36393f;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.upload-button {
  padding: 8px 12px;
  background-color: #4f545c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.upload-button:hover {
  background-color: #5d6269;
}

/* 字符卡片网格 */
.character-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.character-card {
  background-color: #2f3136;
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}

.character-card:hover {
  background-color: #40444b;
  transform: translateY(-2px);
}

.character-card.selected {
  background-color: #5865f2;
}

.character-card .character-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: #40444b;
  margin-bottom: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 24px;
  font-weight: bold;
  color: white;
  overflow: hidden;
}

.character-card .character-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.character-card .character-name {
  font-size: 14px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.character-card .character-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.character-card:hover .character-actions {
  opacity: 1;
}

.action-button {
  width: 24px;
  height: 24px;
  background-color: rgba(0, 0, 0, 0.3);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: background-color 0.2s;
}

.action-button:hover {
  background-color: rgba(0, 0, 0, 0.5);
}

.add-character {
  background-color: #40444b;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #b9bbbe;
}

.add-character:hover {
  background-color: #4f545c;
  color: white;
}

.add-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

/* AI预设界面 */
.presets-container {
  display: flex;
  height: 65vh;
  border: 1px solid #2f3136;
  border-radius: 4px;
  overflow: hidden;
}

.presets-sidebar {
  width: 250px;
  background-color: #2f3136;
  border-right: 1px solid #202225;
  display: flex;
  flex-direction: column;
}

.preset-search {
  padding: 12px;
  border-bottom: 1px solid #202225;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 22px;
  top: 50%;
  transform: translateY(-50%);
  color: #72767d;
}

.clear-icon {
  position: absolute;
  right: 22px;
  top: 50%;
  transform: translateY(-50%);
  color: #72767d;
  cursor: pointer;
}

.clear-icon:hover {
  color: #dcddde;
}

.preset-search-input {
  width: 100%;
  padding: 8px 32px;
  background-color: #40444b;
  border: none;
  border-radius: 4px;
  color: #dcddde;
  font-size: 13px;
}

.preset-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.preset-item {
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 4px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 10px;
}

.preset-item:hover {
  background-color: #40444b;
}

.preset-item.active {
  background-color: #40444b;
}

.preset-icon {
  width: 24px;
  height: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #b9bbbe;
  font-size: 16px;
}

.preset-info {
  flex: 1;
  min-width: 0;
}

.preset-name {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

.preset-tag-more {
  font-size: 11px;
  color: #b9bbbe;
}

.add-preset {
  color: #b9bbbe;
}

.add-preset:hover {
  color: white;
}

.preset-editor {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background-color: #36393f;
}

.preset-editor-content {
  animation: fadeIn 0.2s ease-out;
}

.preset-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.preset-header .setting-item {
  flex: 1;
  margin-bottom: 0;
  margin-right: 16px;
}

.preset-name-input {
  font-size: 16px;
  font-weight: 500;
}

.preset-actions {
  display: flex;
  gap: 8px;
}

.save-preset-button,
.delete-preset-button {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.save-preset-button {
  background-color: #5865f2;
  color: white;
}

.save-preset-button:hover {
  background-color: #4752c4;
}

.delete-preset-button {
  background-color: #4f545c;
  color: #f04747;
}

.delete-preset-button:hover {
  background-color: #f04747;
  color: white;
}

.tags-input {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 12px;
  background-color: #40444b;
  border-radius: 4px;
  min-height: 40px;
  align-items: center;
}

.tag-item {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  background-color: #5865f2;
  border-radius: 12px;
  font-size: 12px;
  color: white;
}

.tag-remove {
  margin-left: 4px;
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
}

.tag-input {
  border: none;
  background: none;
  color: #dcddde;
  flex: 1;
  min-width: 100px;
  outline: none;
  font-size: 12px;
}

.preset-instructions {
  margin-top: 8px;
}

.instruction-item {
  background-color: #2f3136;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.instruction-header {
  padding: 10px 12px;
  background-color: #202225;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.instruction-title {
  font-weight: 500;
  font-size: 14px;
}

.instruction-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.add-instruction-button {
  padding: 6px 10px;
  background-color: #4f545c;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.2s;
}

.add-instruction-button:hover {
  background-color: #5d6269;
}

/* 开关样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #4f545c;
  transition: .4s;
  border-radius: 34px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #5865f2;
}

input:checked + .slider:before {
  transform: translateX(20px);
}

.instruction-remove,
.instruction-expand {
  background: none;
  border: none;
  cursor: pointer;
  width: 24px;
  height: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.instruction-remove {
  color: #b9bbbe;
}

.instruction-remove:hover {
  color: #f04747;
  background-color: rgba(240, 71, 71, 0.1);
}

.instruction-expand {
  color: #b9bbbe;
}

.instruction-expand:hover {
  color: white;
  background-color: rgba(255, 255, 255, 0.1);
}

.instruction-content {
  padding: 12px;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from { opacity: 0; max-height: 0; }
  to { opacity: 1; max-height: 500px; }
}

.instruction-field {
  margin-bottom: 12px;
}

.field-label {
  font-size: 12px;
  color: #b9bbbe;
  margin-bottom: 4px;
}

.instruction-textarea {
  resize: vertical;
  min-height: 100px;
}

.checkbox-field {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
}

/* 提示词顺序部分 */
.preset-order-section {
  margin-top: 20px;
}

.preset-order-list {
  background-color: #2f3136;
  border-radius: 4px;
  padding: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.prompt-order-item {
  padding: 8px 10px;
  background-color: #40444b;
  border-radius: 4px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.drag-handle {
  cursor: move;
  color: #b9bbbe;
}

.prompt-order-name {
  flex: 1;
  font-size: 14px;
}

.ghost {
  opacity: 0.5;
  background: #202225;
}

/* 高级设置 */
.advanced-settings {
  margin-top: 20px;
  background-color: #2f3136;
  border-radius: 4px;
  padding: 16px;
}

.slider-container {
  position: relative;
}

.temperature-slider {
  width: 100%;
  height: 8px;
  -webkit-appearance: none;
  appearance: none;
  background: linear-gradient(to right, #5865f2, #43b581);
  border-radius: 4px;
  outline: none;
}

.temperature-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background-color: white;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #b9bbbe;
}

.slider-value {
  text-align: center;
  margin-top: 4px;
  font-size: 14px;
  color: #dcddde;
}

.no-preset-selected {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #72767d;
}

.no-preset-icon {
  margin-bottom: 16px;
}

.no-preset-text {
  font-size: 16px;
}

/* API 输入组 */
.api-key-input-group {
  display: flex;
  align-items: center;
}

.api-key-input {
  flex: 1;
  border-radius: 4px 0 0 4px;
  font-family: monospace;
}

.show-key-button {
  padding: 10px 12px;
  background-color: #4f545c;
  border: none;
  border-radius: 0 4px 4px 0;
  color: #b9bbbe;
  cursor: pointer;
  transition: all 0.2s;
}

.show-key-button:hover {
  background-color: #5d6269;
  color: white;
}

/* 模型设置样式 */
.provider-select {
  margin-bottom: 16px;
}

.api-settings {
  background-color: #2f3136;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 20px;
}

/* TTS设置 */
.tts-status {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #2f3136;
  border-radius: 4px;
  margin-bottom: 16px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.status-indicator.online {
  color: #43b581;
}

.status-indicator.offline {
  color: #f04747;
}

.check-connection-button {
  padding: 6px 12px;
  background-color: #4f545c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  transition: all 0.2s;
}

.check-connection-button:hover {
  background-color: #5d6269;
}

.url-input-group {
  display: flex;
  gap: 8px;
}

.tts-url-input {
  flex: 1;
}

.save-url-button {
  padding: 0 12px;
  background-color: #5865f2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}

.save-url-button:hover {
  background-color: #4752c4;
}

.tts-settings {
  animation: fadeIn 0.3s ease-out;
}

.tts-slider {
  width: 100%;
  -webkit-appearance: none;
  height: 8px;
  border-radius: 4px;
  background: #4f545c;
  outline: none;
}

.tts-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #5865f2;
  cursor: pointer;
}

.checkbox-option {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
}

.ref-audio-controls {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ref-audio-file {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: #40444b;
  border-radius: 4px;
  font-size: 14px;
}

.play-button {
  margin-left: auto;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #5865f2;
  color: white;
  border: none;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
}

.play-button:hover {
  background-color: #4752c4;
}

/* 主题选项 */
.theme-options {
  display: flex;
  gap: 12px;
}

.theme-option {
  flex: 1;
  padding: 10px;
  background-color: #2f3136;
  border: 1px solid #40444b;
  border-radius: 4px;
  color: #dcddde;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.theme-option:hover {
  background-color: #40444b;
}

.theme-option.active {
  background-color: #5865f2;
  border-color: #5865f2;
  color: white;
}

/* 页脚 */
.settings-footer {
  padding: 16px 20px;
  background-color: #2f3136;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  border-top: 1px solid #202225;
}

.cancel-button,
.save-button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.cancel-button {
  background-color: #4f545c;
  color: #dcddde;
}

.cancel-button:hover {
  background-color: #5d6269;
}

.save-button {
  background-color: #5865f2;
  color: white;
}

.save-button:hover {
  background-color: #4752c4;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1002;
}

.modal-container {
  width: 500px;
  max-width: 95%;
  background-color: #36393f;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  padding: 16px;
  border-bottom: 1px solid #2f3136;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  color: #fff;
  border-bottom: none;
  padding-bottom: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-content {
  padding: 16px;
}

.input-field,
.textarea-field {
  width: 100%;
  padding: 10px;
  border: none;
  background-color: #40444b;
  color: #dcddde;
  border-radius: 4px;
  font-size: 14px;
  margin-bottom: 16px;
}

.textarea-field {
  resize: vertical;
  min-height: 100px;
}

.modal-footer {
  padding: 16px;
  border-top: 1px solid #2f3136;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.confirm-button {
  padding: 8px 16px;
  background-color: #5865f2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.confirm-button:hover {
  background-color: #4752c4;
}

/* 响应式样式 */
@media (max-width: 768px) {
  .settings-container {
    width: 100%;
    height: 100%;
    max-width: 100%;
    border-radius: 0;
  }

  .character-grid {
    grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
  }

  .presets-container {
    flex-direction: column;
    height: auto;
  }

  .presets-sidebar {
    width: 100%;
    height: auto;
    max-height: 200px;
  }

  .preset-editor {
    padding: 12px;
  }

  .settings-tabs {
    overflow-x: auto;
    padding: 4px 8px;
  }

  .settings-tabs button {
    padding: 8px 12px;
  }

  .tab-name {
    display: none;
  }

  .preset-header {
    flex-direction: column;
  }

  .preset-header .setting-item {
    margin-right: 0;
    margin-bottom: 12px;
  }

  .preset-actions {
    justify-content: space-between;
    width: 100%;
  }
}
</style>