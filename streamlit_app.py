<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>좀비 슈터 RPG</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Inter 폰트 로드 */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        body {
            font-family: 'Inter', sans-serif;
            background-color: #1a202c; /* Tailwind gray-900 */
            color: #e2e8f0; /* Tailwind gray-200 */
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            overflow: hidden; /* 스크롤바 방지 */
        }
        #game-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: #2d3748; /* Tailwind gray-800 */
            border-radius: 1rem; /* rounded-xl */
            padding: 1.5rem; /* p-6 */
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.25); /* shadow-xl */
            width: 90vw; /* 가변 너비 */
            max-width: 1000px; /* 최대 너비 제한 */
        }
        canvas {
            background-color: #1a202c; /* 게임 배경 */
            border: 2px solid #4a5568; /* Tailwind gray-600 */
            border-radius: 0.5rem; /* rounded-md */
            display: block;
            touch-action: none; /* 터치 이벤트 기본 동작 방지 (캔버스 드래그 등) */
        }
        #ui-panel {
            display: flex;
            justify-content: space-between;
            width: 100%;
            margin-top: 1rem; /* mt-4 */
            gap: 1rem;
            flex-wrap: wrap; /* 작은 화면에서 요소들이 줄바꿈되도록 */
        }
        .ui-element {
            background-color: #4a5568; /* Tailwind gray-600 */
            padding: 0.75rem 1rem; /* py-3 px-4 */
            border-radius: 0.5rem; /* rounded-md */
            text-align: center;
            font-weight: bold;
            flex: 1; /* 가변 너비 */
            min-width: 120px; /* 최소 너비 설정 */
        }
        .ui-element span {
            display: block;
            font-size: 0.875rem; /* text-sm */
            color: #a0aec0; /* Tailwind gray-400 */
        }
        #message-box {
            background-color: #2c5282; /* Tailwind blue-700 */
            color: #fff;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-top: 1rem;
            width: 100%;
            text-align: center;
            font-weight: bold;
            display: none; /* 초기에는 숨김 */
            position: absolute; /* 캔버스 위에 오도록 */
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 100;
            opacity: 0;
            transition: opacity 0.3s ease-in-out;
        }
        #message-box.active {
            display: block;
            opacity: 1;
        }
        .game-button {
            background-color: #38a169; /* Tailwind green-600 */
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.2s;
            margin-top: 1rem;
        }
        .game-button:hover {
            background-color: #2f855a; /* Tailwind green-700 */
        }
        .game-button:disabled {
            background-color: #a0aec0; /* Tailwind gray-400 */
            cursor: not-allowed;
        }
        #game-over-screen, #game-win-screen {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            font-size: 2rem;
            text-align: center;
            z-index: 200;
            opacity: 0;
            pointer-events: none; /* 초기에는 클릭 불가능 */
            transition: opacity 0.5s ease-in-out;
            border-radius: 1rem; /* rounded-xl */
        }
        #game-over-screen.active, #game-win-screen.active {
            opacity: 1;
            pointer-events: auto; /* 활성화 시 클릭 가능 */
        }
        #game-over-screen h2, #game-win-screen h2 {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        #game-win-screen h2 {
            color: #48bb78; /* Tailwind green-500 */
        }
    </style>
</head>
<body>
    <div id="game-container" class="relative">
        <canvas id="gameCanvas"></canvas>
        <div id="ui-panel">
            <div class="ui-element">HP: <span id="playerHp">100</span></div>
            <div class="ui-element">탄약: <span id="playerAmmo">6 / 30</span></div>
            <div class="ui-element">골드: <span id="playerGold">0</span></div>
            <div class="ui-element">킬 수: <span id="playerKills">0</span></div>
        </div>
        <button id="reloadButton" class="game-button">재장전 (R)</button>

        <div id="message-box" class="rounded-lg"></div>

        <div id="game-over-screen" class="rounded-xl">
            <h2>게임 오버!</h2>
            <p>모든 좀비로부터 살아남지 못했습니다.</p>
            <button id="restartGameBtn" class="game-button">다시 시작</button>
        </div>
        
        <div id="game-win-screen" class="rounded-xl">
            <h2>게임 클리어!</h2>
            <p>모든 좀비를 물리쳤습니다!</p>
            <button id="restartWinBtn" class="game-button">다시 시작</button>
        </div>
    </div>

    <script>
        // 캔버스 및 컨텍스트 설정
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        // UI 요소
        const playerHpEl = document.getElementById('playerHp');
        const playerAmmoEl = document.getElementById('playerAmmo');
        const playerGoldEl = document.getElementById('playerGold');
        const playerKillsEl = document.getElementById('playerKills');
        const reloadButton = document.getElementById('reloadButton');
        const messageBox = document.getElementById('message-box');
        const gameOverScreen = document.getElementById('game-over-screen');
        const gameWinScreen = document.getElementById('game-win-screen');
        const restartGameBtn = document.getElementById('restartGameBtn');
        const restartWinBtn = document.getElementById('restartWinBtn');

        // 게임 변수
        let gameRunning = false;
        let animationFrameId;

        // 플레이어 설정
        const player = {
            x: 0,
            y: 0,
            radius: 15,
            hp: 100,
            maxHp: 100,
            baseAtk: 10,
            color: '#4299e1', // Tailwind blue-500
            currentMagAmmo: 6,
            magazineSize: 6,
            totalAmmo: 30,
            fireRate: 200, // ms, 샷 간 지연
            lastShotTime: 0,
            reloadTime: 1500, // ms
            isReloading: false,
            gold: 0,
            kills: 0
        };

        // 마우스 위치
        const mouse = {
            x: 0,
            y: 0
        };

        // 총알 배열
        let bullets = [];
        const bulletSpeed = 10;
        const bulletRadius = 3;

        // 좀비 배열
        let zombies = [];
        let zombieSpawnTimer = 0;
        const zombieSpawnInterval = 1000; // ms
        let zombiesPerWave = 1;
        let waveCount = 0;
        const maxWaves = 10; // 최종 보스 전까지 웨이브 수
        const zombieMaxHp = 30; // 시작 좀비 HP
        const zombieBaseAtk = 5; // 시작 좀비 공격력
        const zombieSpeed = 1; // 시작 좀비 속도

        // 아이템 배열
        let items = [];
        const itemSpawnInterval = 5000; // ms
        let itemSpawnTimer = 0;
        const itemRadius = 10;

        // 메시지 박스 타이머
        let messageTimeout;

        // ======================================
        // 게임 유틸리티 함수
        // ======================================

        /**
         * 메시지 박스를 화면에 표시하고 일정 시간 후 사라지게 합니다.
         * @param {string} msg - 표시할 메시지
         * @param {number} duration - 메시지가 표시될 시간 (ms)
         */
        function showMessage(msg, duration = 1500) {
            clearTimeout(messageTimeout); // 기존 타이머 클리어
            messageBox.textContent = msg;
            messageBox.classList.add('active');
            messageTimeout = setTimeout(() => {
                messageBox.classList.remove('active');
            }, duration);
        }

        /**
         * 충돌 감지 (원-원)
         * @param {object} obj1 - 첫 번째 객체 {x, y, radius}
         * @param {object} obj2 - 두 번째 객체 {x, y, radius}
         * @returns {boolean} 충돌 여부
         */
        function checkCollision(obj1, obj2) {
            const dx = obj1.x - obj2.x;
            const dy = obj1.y - obj2.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            return distance < (obj1.radius + obj2.radius);
        }

        /**
         * UI를 업데이트합니다.
         */
        function updateUI() {
            playerHpEl.textContent = `${Math.max(0, player.hp)} / ${player.maxHp}`;
            playerAmmoEl.textContent = `${player.currentMagAmmo} / ${player.totalAmmo}`;
            playerGoldEl.textContent = player.gold;
            playerKillsEl.textContent = player.kills;

            // 재장전 버튼 상태 업데이트
            if (player.currentMagAmmo === player.magazineSize || player.totalAmmo === 0 || player.isReloading) {
                reloadButton.disabled = true;
            } else {
                reloadButton.disabled = false;
            }
        }

        // ======================================
        // 게임 객체 정의 (생성자)
        // ======================================

        /**
         * 총알 객체
         * @param {number} x - 초기 x 좌표
         * @param {number} y - 초기 y 좌표
         * @param {number} angle - 발사 각도
         * @param {number} damage - 공격력
         */
        function Bullet(x, y, angle, damage) {
            this.x = x;
            this.y = y;
            this.radius = bulletRadius;
            this.vx = Math.cos(angle) * bulletSpeed;
            this.vy = Math.sin(angle) * bulletSpeed;
            this.damage = damage;
            this.color = '#f56565'; // Tailwind red-500

            this.update = function() {
                this.x += this.vx;
                this.y += this.vy;
            };

            this.draw = function() {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fill();
            };
        }

        /**
         * 좀비 객체
         * @param {number} x - 초기 x 좌표
         * @param {number} y - 초기 y 좌표
         * @param {number} hp - 체력
         * @param {number} atk - 공격력
         * @param {number} speed - 이동 속도
         * @param {number} gold - 처치 시 획득 골드
         * @param {number} id - 고유 ID (Streamlit key 문제 해결을 위한 임시 방편)
         */
        let zombieIdCounter = 0; // 좀비 고유 ID 카운터
        function Zombie(x, y, hp, atk, speed, gold) {
            this.x = x;
            this.y = y;
            this.radius = 20;
            this.hp = hp;
            this.maxHp = hp;
            this.atk = atk;
            this.speed = speed;
            this.color = '#4c51bf'; // Tailwind indigo-600
            this.gold = gold;
            this.id = zombieIdCounter++; // 고유 ID 부여

            this.update = function() {
                // 플레이어를 향해 이동
                const angle = Math.atan2(player.y - this.y, player.x - this.x);
                this.x += Math.cos(angle) * this.speed;
                this.y += Math.sin(angle) * this.speed;

                // 플레이어와 충돌 시 공격
                if (checkCollision(this, player)) {
                    player.hp -= this.atk;
                    log(`좀비가 ${this.atk} 피해를 입혔습니다!`);
                    // 플레이어 체력 음수 방지
                    if (player.hp <= 0) {
                        player.hp = 0;
                        gameOver();
                    }
                    // 충돌 후 좀비 위치 약간 밀어내기
                    const overlap = (this.radius + player.radius) - Math.sqrt(Math.pow(this.x - player.x, 2) + Math.pow(this.y - player.y, 2));
                    this.x += Math.cos(angle) * -overlap;
                    this.y += Math.sin(angle) * -overlap;
                }
            };

            this.draw = function() {
                // 좀비 몸통
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fill();

                // HP 바
                const barWidth = this.radius * 2;
                const barHeight = 5;
                const hpRatio = this.hp / this.maxHp;
                ctx.fillStyle = 'gray';
                ctx.fillRect(this.x - this.radius, this.y - this.radius - barHeight - 2, barWidth, barHeight);
                ctx.fillStyle = 'lime';
                ctx.fillRect(this.x - this.radius, this.y - this.radius - barHeight - 2, barWidth * hpRatio, barHeight);
            };
        }

        /**
         * 아이템 객체 (회복 포션, 탄약)
         * @param {number} x - 초기 x 좌표
         * @param {number} y - 초기 y 좌표
         * @param {string} type - 아이템 타입 ('health', 'ammo')
         */
        function Item(x, y, type) {
            this.x = x;
            this.y = y;
            this.radius = itemRadius;
            this.type = type;
            this.color = type === 'health' ? '#f6e05e' : '#a0aec0'; // Tailwind yellow-400 or gray-400

            this.draw = function() {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fill();
                // 아이템 아이콘 (간단한 텍스트)
                ctx.fillStyle = '#1a202c';
                ctx.font = 'bold 12px Inter';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(this.type === 'health' ? '❤️' : '➕', this.x, this.y);
            };
        }

        // ======================================
        // 게임 로직 함수
        // ======================================

        /**
         * 캔버스 크기를 화면에 맞게 조정하고 플레이어 위치를 초기화합니다.
         */
        function resizeCanvas() {
            canvas.width = window.innerWidth * 0.8; // 화면 너비의 80%
            canvas.height = window.innerHeight * 0.7; // 화면 높이의 70%

            // 최소 크기 제한
            if (canvas.width < 600) canvas.width = 600;
            if (canvas.height < 400) canvas.height = 400;

            // 플레이어 초기 위치를 캔버스 중앙으로 설정
            player.x = canvas.width / 2;
            player.y = canvas.height / 2;

            updateUI(); // UI 업데이트
        }

        /**
         * 게임 초기화 함수
         */
        function initGame() {
            // 플레이어 상태 초기화
            player.hp = player.maxHp;
            player.currentMagAmmo = player.magazineSize;
            player.totalAmmo = 30; // 초기 탄약
            player.gold = 0;
            player.kills = 0;
            player.isReloading = false;
            player.lastShotTime = 0;

            // 게임 요소 초기화
            bullets = [];
            zombies = [];
            items = [];
            zombieSpawnTimer = 0;
            itemSpawnTimer = 0;
            waveCount = 0;
            zombiesPerWave = 1;
            zombieIdCounter = 0; // 좀비 ID 카운터 초기화

            // UI 및 화면 초기화
            showMessage("게임을 시작합니다!", 2000);
            gameOverScreen.classList.remove('active');
            gameWinScreen.classList.remove('active');
            
            resizeCanvas(); // 캔버스 크기 조정 및 플레이어 위치 설정

            if (!gameRunning) {
                gameRunning = true;
                gameLoop(); // 게임 루프 시작
            }
        }

        /**
         * 플레이어 총 발사 로직
         */
        function shoot() {
            const now = Date.now();
            if (player.currentMagAmmo > 0 && !player.isReloading && (now - player.lastShotTime > player.fireRate)) {
                // 마우스와 플레이어 사이의 각도 계산
                const angle = Math.atan2(mouse.y - player.y, mouse.x - player.x);
                bullets.push(new Bullet(player.x, player.y, angle, player.baseAtk));
                player.currentMagAmmo--;
                player.lastShotTime = now;
                updateUI();
            } else if (player.currentMagAmmo === 0 && !player.isReloading) {
                showMessage("탄약이 없습니다! 재장전하세요 (R)", 1000);
            }
        }

        /**
         * 플레이어 재장전 로직
         */
        function reload() {
            if (player.isReloading || player.currentMagAmmo === player.magazineSize || player.totalAmmo === 0) {
                return; // 이미 재장전 중이거나, 탄창이 가득 찼거나, 전체 탄약이 없으면 재장전 불가
            }

            player.isReloading = true;
            showMessage("재장전 중...", player.reloadTime);
            reloadButton.disabled = true; // 재장전 중 버튼 비활성화

            setTimeout(() => {
                const ammoToReload = Math.min(player.magazineSize - player.currentMagAmmo, player.totalAmmo);
                player.currentMagAmmo += ammoToReload;
                player.totalAmmo -= ammoToReload;
                player.isReloading = false;
                showMessage("재장전 완료!", 500);
                updateUI();
            }, player.reloadTime);
        }

        /**
         * 좀비를 생성합니다.
         */
        function createZombie() {
            let x, y;
            // 화면 가장자리에서 생성
            const side = Math.floor(Math.random() * 4); // 0: top, 1: right, 2: bottom, 3: left
            if (side === 0) { // top
                x = Math.random() * canvas.width;
                y = -50;
            } else if (side === 1) { // right
                x = canvas.width + 50;
                y = Math.random() * canvas.height;
            } else if (side === 2) { // bottom
                x = Math.random() * canvas.width;
                y = canvas.height + 50;
            } else { // left
                x = -50;
                y = Math.random() * canvas.height;
            }

            // 웨이브 진행에 따라 좀비 능력치 강화
            const hpBoost = waveCount * 5;
            const atkBoost = Math.floor(waveCount / 2);
            const speedBoost = waveCount * 0.1;

            zombies.push(new Zombie(
                x, y,
                zombieMaxHp + hpBoost,
                zombieBaseAtk + atkBoost,
                zombieSpeed + speedBoost,
                random.randint(5, 15) + Math.floor(waveCount / 3) // 골드 보너스
            ));
        }

        /**
         * 아이템을 생성합니다.
         */
        function createItem() {
            const x = Math.random() * (canvas.width - itemRadius * 2) + itemRadius;
            const y = Math.random() * (canvas.height - itemRadius * 2) + itemRadius;
            const type = random.choice(['health', 'ammo']); // 'health' 또는 'ammo'
            items.push(new Item(x, y, type));
        }

        /**
         * 게임 오버 처리
         */
        function gameOver() {
            gameRunning = false;
            cancelAnimationFrame(animationFrameId); // 게임 루프 중지
            gameOverScreen.classList.add('active'); // 게임 오버 화면 활성화
            showMessage("게임 오버!", 3000);
        }

        /**
         * 게임 클리어 처리 (예시, 특정 조건 달성 시 호출)
         */
        function gameWin() {
            gameRunning = false;
            cancelAnimationFrame(animationFrameId);
            gameWinScreen.classList.add('active');
            showMessage("게임 클리어!", 3000);
        }

        // ======================================
        // 메인 게임 루프
        // ======================================

        let lastTime = 0;
        function gameLoop(currentTime) {
            if (!gameRunning) return;

            const deltaTime = currentTime - lastTime;
            lastTime = currentTime;

            // 업데이트
            update(deltaTime);
            // 그리기
            draw();

            animationFrameId = requestAnimationFrame(gameLoop);
        }

        /**
         * 모든 게임 요소의 상태를 업데이트합니다.
         * @param {number} deltaTime - 마지막 업데이트 이후 경과 시간 (ms)
         */
        function update(deltaTime) {
            // 좀비 생성 타이머
            zombieSpawnTimer += deltaTime;
            if (zombieSpawnTimer >= zombieSpawnInterval && waveCount < maxWaves) {
                for (let i = 0; i < zombiesPerWave; i++) {
                    createZombie();
                }
                zombieSpawnTimer = 0;
                // 웨이브 진행에 따라 좀비 생성 수 증가
                waveCount++;
                if (waveCount % 2 === 0) { // 2웨이브마다 생성 좀비 수 증가
                    zombiesPerWave++;
                }
                if (waveCount === maxWaves) {
                    // 마지막 웨이브 후 모든 좀비 처치 시 게임 클리어 고려 (예시)
                    showMessage("최종 웨이브! 모든 좀비를 처치하세요!", 2000);
                }
            }
            // 모든 좀비 처치 및 최종 웨이브 달성 시 게임 클리어 (예시)
            if (waveCount === maxWaves && zombies.length === 0) {
                 gameWin();
            }


            // 아이템 생성 타이머
            itemSpawnTimer += deltaTime;
            if (itemSpawnTimer >= itemSpawnInterval) {
                createItem();
                itemSpawnTimer = 0;
            }

            // 총알 업데이트 및 경계 검사
            bullets = bullets.filter(bullet => {
                bullet.update();
                // 캔버스 밖으로 나가면 제거
                return bullet.x > -bullet.radius && bullet.x < canvas.width + bullet.radius &&
                       bullet.y > -bullet.radius && bullet.y < canvas.height + bullet.radius;
            });

            // 좀비 업데이트
            zombies.forEach(zombie => zombie.update());

            // 플레이어 HP 업데이트 (UI)
            updateUI();

            // 충돌 감지
            checkCollisions();
        }

        /**
         * 모든 게임 요소를 캔버스에 그립니다.
         */
        function draw() {
            // 캔버스 지우기
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 플레이어 그리기
            ctx.fillStyle = player.color;
            ctx.beginPath();
            ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2);
            ctx.fill();

            // 플레이어 조준선 (마우스를 향해)
            const angle = Math.atan2(mouse.y - player.y, mouse.x - player.x);
            ctx.strokeStyle = '#e2e8f0'; // Tailwind gray-200
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(player.x, player.y);
            ctx.lineTo(player.x + Math.cos(angle) * player.radius * 2, player.y + Math.sin(angle) * player.radius * 2);
            ctx.stroke();

            // 총알 그리기
            bullets.forEach(bullet => bullet.draw());

            // 좀비 그리기
            zombies.forEach(zombie => zombie.draw());

            // 아이템 그리기
            items.forEach(item => item.draw());
        }

        /**
         * 모든 충돌을 감지하고 처리합니다.
         */
        function checkCollisions() {
            // 총알-좀비 충돌
            for (let i = bullets.length - 1; i >= 0; i--) {
                for (let j = zombies.length - 1; j >= 0; j--) {
                    if (checkCollision(bullets[i], zombies[j])) {
                        zombies[j].hp -= bullets[i].damage;
                        bullets.splice(i, 1); // 총알 제거
                        
                        if (zombies[j].hp <= 0) {
                            player.gold += zombies[j].gold; // 골드 획득
                            player.kills++; // 킬 수 증가
                            log(`${zombies[j].name} 처치! 골드 +${zombies[j].gold}, 킬 수 +1`);
                            zombies.splice(j, 1); // 좀비 제거
                        }
                        break; // 총알이 하나의 좀비에만 명중하도록
                    }
                }
            }

            // 플레이어-아이템 충돌
            for (let i = items.length - 1; i >= 0; i--) {
                if (checkCollision(player, items[i])) {
                    if (items[i].type === 'health') {
                        const healAmount = 50;
                        player.hp = Math.min(player.maxHp, player.hp + healAmount);
                        showMessage(`HP +${healAmount}!`, 1000);
                    } else if (items[i].type === 'ammo') {
                        const ammoAmount = 15;
                        player.totalAmmo = Math.min(999, player.totalAmmo + ammoAmount); // 최대 탄약 제한
                        showMessage(`탄약 +${ammoAmount}!`, 1000);
                    }
                    items.splice(i, 1); // 아이템 제거
                    updateUI();
                }
            }
        }

        // ======================================
        // 이벤트 리스너
        // ======================================

        // 캔버스 크기 변경 시 재조정
        window.addEventListener('resize', resizeCanvas);

        // 마우스 이동 시 플레이어 조준 업데이트
        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            mouse.x = e.clientX - rect.left;
            mouse.y = e.clientY - rect.top;
        });

        // 마우스 클릭 시 총 발사
        canvas.addEventListener('mousedown', (e) => {
            if (e.button === 0) { // 좌클릭
                shoot();
            }
        });

        // 키보드 입력
        window.addEventListener('keydown', (e) => {
            if (e.key === 'r' || e.key === 'R') {
                reload();
            }
        });

        // UI 버튼 클릭
        reloadButton.addEventListener('click', reload);
        restartGameBtn.addEventListener('click', initGame);
        restartWinBtn.addEventListener('click', initGame);

        // ======================================
        // 게임 시작
        // ======================================
        window.onload = function() {
            initGame(); // 페이지 로드 완료 후 게임 초기화 및 시작
        };

        // --- Streamlit `random.randint` 및 `random.choice` 대체 ---
        // Canvas 환경에서 Streamlit의 random 함수를 직접 사용할 수 없으므로,
        // JavaScript의 Math.random을 사용하여 동일한 기능을 구현합니다.
        
        // Python random.randint(a, b)와 유사한 기능
        random.randint = function(min, max) {
            min = Math.ceil(min);
            max = Math.floor(max);
            return Math.floor(Math.random() * (max - min + 1)) + min;
        };

        // Python random.choice(array)와 유사한 기능
        random.choice = function(arr) {
            return arr[Math.floor(Math.random() * arr.length)];
        };

    </script>
</body>
</html>