let currentPage = 0;
const itemsPerPage = 6;
let skillsPage = 0;
const skillsPerPage = 6;
let selectedSkills = [];

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('collapsed');
}

// 页面加载时自动折叠侧边栏
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.add('collapsed');
});

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.style.display = 'block';
    if (modalId === 'inventoryModal') {
        loadInventory();
    } else if (modalId === 'containerModal') {
        loadContainer('trunk');
    } else if (modalId === 'spellsModal') {
        currentPage = 1;
        loadSpells(currentPage);
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.style.display = 'none';
}

function loadSpells(page) {
    fetch('/get_spells')
        .then(response => response.json())
        .then(data => {
            const spellsList = document.getElementById('spells-list');
            spellsList.innerHTML = '';
            const start = (page - 1) * itemsPerPage;
            const end = start + itemsPerPage;
            const paginatedSpells = data.spells.slice(start, end);

            if (paginatedSpells.length === 0) {
                spellsList.innerHTML = '<div class="empty-message">你还未学会任何咒语</div>';
            } else {
                paginatedSpells.forEach(spell => {
                    const spellDiv = document.createElement('div');
                    spellDiv.className = 'inventory-item';
                    spellDiv.innerHTML = `
                        <div class="item-icon">🪄</div>
                        <div class="item-name">${spell.name}</div>
                        <div class="item-description">${spell.description}</div>`;
                    spellsList.appendChild(spellDiv);
                });
            }

            updateSpellsPagination(data.spells.length, page);
        });
}

function loadSkills() {
    fetch('/get_spells')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('skillsContainer');
            container.innerHTML = '';
            const start = skillsPage * skillsPerPage;
            const end = start + skillsPerPage;
            const paginatedSkills = data.spells.slice(start, end);

            if (paginatedSkills.length === 0) {
                container.innerHTML = '<div class="empty-message">你还未学会任何战斗技能</div>';
            } else {
                paginatedSkills.forEach(spell => {
                    const div = document.createElement('div');
                    div.className = 'inventory-item';
                    div.innerHTML = `
                        <div class="item-icon">⚔️</div>
                        <div class="item-name">${spell.name}</div>
                        <div class="item-description">${spell.description}</div>
                        <div class="item-actions">
                            <button class="action-button" onclick="toggleSkill('${spell.name}', this)">${selectedSkills.includes(spell.name) ? '取消' : '选择'}</button>
                        </div>`;
                    container.appendChild(div);
                });
            }

            document.getElementById('prevSkillsButton').disabled = skillsPage === 0;
            document.getElementById('nextSkillsButton').disabled = end >= data.spells.length;
        });
}

function toggleSkill(skillName, button) {
    const index = selectedSkills.indexOf(skillName);
    if (index === -1 && selectedSkills.length < 3) {
        selectedSkills.push(skillName);
        button.textContent = '取消';
    } else if (index !== -1) {
        selectedSkills.splice(index, 1);
        button.textContent = '选择';
    } else {
        alert('最多选择3个技能！');
    }
}

function confirmSkillsSelection() {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/select_skills';
    selectedSkills.forEach(skill => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'skills';
        input.value = skill;
        form.appendChild(input);
    });
    document.body.appendChild(form);
    form.submit();
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        loadSpells(currentPage);
    }
}

function nextPage() {
    fetch('/get_spells')
        .then(response => response.json())
        .then(data => {
            const totalPages = Math.ceil(data.spells.length / itemsPerPage);
            if (currentPage < totalPages) {
                currentPage++;
                loadSpells(currentPage);
            }
        });
}

function prevSkillsPage() {
    if (skillsPage > 0) {
        skillsPage--;
        loadSkills();
    }
}

function nextSkillsPage() {
    fetch('/get_spells')
        .then(response => response.json())
        .then(data => {
            const totalPages = Math.ceil(data.spells.length / skillsPerPage);
            if (skillsPage < totalPages) {
                skillsPage++;
                loadSkills();
            }
        });
}

function chooseBattleAction(choiceIndex) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/battle_choose';
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'choice';
    input.value = choiceIndex;
    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
}

function loadInventory() {
    fetch('/scene_container/inventory')
        .then(response => response.json())
        .then(data => {
            const inventoryContainer = document.getElementById('inventory');
            inventoryContainer.innerHTML = '';

            if (Object.keys(data.inventory).length === 0) {
                inventoryContainer.innerHTML = '<div class="empty-message">背包是空的</div>';
            } else {
                for (let [item, quantity] of Object.entries(data.inventory)) {
                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'inventory-item';
                    itemDiv.innerHTML = `
                        <div class="item-icon">🎒</div>
                        <div class="item-name">${item} (x${quantity})</div>
                        <div class="item-actions">
                            <button class="action-button" onclick="itemAction('use', '${item}')">使用/穿戴</button>
                            <button class="action-button" onclick="itemAction('discard', '${item}')">丢弃</button>
                        </div>`;
                    inventoryContainer.appendChild(itemDiv);
                }
            }

            updateInventoryStats(data.inventory_length);
        });
}

function loadContainer(containerId) {
    fetch(`/scene_container/${containerId}`)
        .then(response => response.json())
        .then(data => {
            const trunkItems = document.getElementById('trunk-items');
            const inventoryItems = document.getElementById('inventory-items');
            trunkItems.innerHTML = '';
            inventoryItems.innerHTML = '';

            if (Object.keys(data.items).length === 0) {
                trunkItems.innerHTML = '<div class="empty-message">容器是空的</div>';
            } else {
                for (let [item, quantity] of Object.entries(data.items)) {
                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'inventory-item';
                    itemDiv.innerHTML = `
                        <div class="item-icon">🎒</div>
                        <div class="item-name">${item} (x${quantity})</div>
                        <div class="item-actions">
                            <button class="action-button" onclick="itemAction('move_to_inventory', '${item}', '${containerId}')">取出</button>
                            <button class="action-button" onclick="itemAction('discard', '${item}', '${containerId}')">丢弃</button>
                        </div>`;
                    trunkItems.appendChild(itemDiv);
                }
            }

            if (Object.keys(data.inventory).length === 0) {
                inventoryItems.innerHTML = '<div class="empty-message">背包是空的</div>';
            } else {
                for (let [item, quantity] of Object.entries(data.inventory)) {
                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'inventory-item';
                    itemDiv.innerHTML = `
                        <div class="item-icon">🎒</div>
                        <div class="item-name">${item} (x${quantity})</div>
                        <div class="item-actions">
                            <button class="action-button" onclick="itemAction('move_to_container', '${item}', '${containerId}')">放入容器</button>
                        </div>`;
                    inventoryItems.appendChild(itemDiv);
                }
            }

            updateInventoryStats(data.inventory_length);
        });
}

function updateInventoryStats(length) {
    const statsElement = document.querySelector('.inventory-stats');
    statsElement.innerHTML = `背包容量: <span class="${length < 8 ? 'good' : 'warning'}">${length}/10</span>`;
}

function updateSpellsPagination(totalItems, currentPage) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    document.getElementById('spells-page-info').textContent = `第 ${currentPage} 页 / 共 ${totalPages} 页`;
    document.getElementById('prevButton').disabled = currentPage === 1;
    document.getElementById('nextButton').disabled = currentPage === totalPages;
}

function showEventMessage(message) {
    const eventDiv = document.createElement('div');
    eventDiv.className = 'event-message';
    eventDiv.textContent = message;
    const sceneTitle = document.querySelector('.scene-title');
    sceneTitle.parentNode.insertBefore(eventDiv, sceneTitle.nextSibling);
    setTimeout(() => eventDiv.remove(), 3000);
}

function itemAction(action, item, container = '') {
    fetch('/item_action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `action=${action}&item=${encodeURIComponent(item)}&container=${container}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.event_message) {
            showEventMessage(data.event_message);
        }
        if (action === 'discard' || action === 'use') {
            loadInventory();
        }
        if (container) {
            loadContainer(container);
        }
        updateStats(data.stats, data.equipment);
    });
}

function showTab(tabId) {
    document.querySelectorAll('.items-container').forEach(tab => tab.style.display = 'none');
    document.getElementById(tabId).style.display = 'grid';
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
}

function updateStats(stats, equipment) {
    document.querySelector('.stat-value[style*="health"]').style.width = `${stats.health}%`;
    document.querySelector('.stat-number:not(:nth-child(2)):not(:nth-child(3))').textContent = `${stats.health}/100`;
    document.querySelector('.stat-value[style*="san"]').style.width = `${stats.san}%`;
    document.querySelector('.stat-number:nth-child(2)').textContent = `${stats.san}/100`;
    document.querySelector('.stat-value[style*="fatigue"]').style.width = `${stats.fatigue}%`;
    document.querySelector('.stat-number:nth-child(3)').textContent = `${stats.fatigue}/100`;
    document.querySelector('.stat:nth-child(4) .stat-label').textContent = `加隆: ${stats.galleons}`;
    document.querySelector('.stat:nth-child(5) .stat-label').textContent = `西可: ${stats.sickle}`;
    document.querySelector('.stat:nth-child(6) .stat-label').textContent = `纳特: ${stats.knut}`;
    document.querySelector('.stat:nth-child(7) .stat-label').textContent = `时间: ${stats.time}`;
    document.querySelector('.stat:nth-child(8) .stat-label').textContent = `敌人血量: ${stats.enemy_health}/${stats.enemy_max_health}`;
    document.querySelector('.inventory li:nth-child(1)').textContent = `手部: ${equipment.hand || '空'}`;
    document.querySelector('.inventory li:nth-child(2)').textContent = `身体: ${equipment.body || '空'}`;
}

function reloadScenes() {
    fetch('/reload_scenes')
        .then(response => response.text())
        .then(message => showEventMessage(message));
}

function gainAllSpells() {
    fetch('/gain_all_spells', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showEventMessage(data.message);
            if (document.getElementById('spellsModal').style.display === 'block') {
                loadSpells(currentPage);
            }
        });
}

function restoreStats() {
    fetch('/restore_stats', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showEventMessage(data.message);
            location.reload();
        });
}

// 成就功能
function openAchievementsModal() {
    document.getElementById('achievementsModal').style.display = 'block';
    loadAchievements();
}

function loadAchievements() {
    fetch('/get_achievements')
        .then(response => response.json())
        .then(data => {
            const achievementsList = document.getElementById('achievements-list');
            achievementsList.innerHTML = '';
            
            if (data.achievements.length === 0) {
                achievementsList.innerHTML = '<div class="empty-message">你还未获得任何成就</div>';
            } else {
                data.achievements.forEach(achievement => {
                    const achievementDiv = document.createElement('div');
                    achievementDiv.className = 'inventory-item';
                    achievementDiv.innerHTML = `
                        <div class="item-icon">🏆</div>
                        <div class="item-name">${achievement.name}</div>
                        <div class="item-description">${achievement.description}</div>`;
                    achievementsList.appendChild(achievementDiv);
                });
            }
        });
}

// 页面加载时自动加载技能列表
document.addEventListener('DOMContentLoaded', () => {
    loadSkills();
});