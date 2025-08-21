import streamlit as st
import random
import time

# =========================
# 초기 설정 및 상수
# =========================
# 게임 상태를 저장할 세션 스테이트 키
STATE_KEYS = [
    "player_hp", "player_max_hp", "player_current_mag_ammo",
    "player_magazine_size", "player_total_ammo", "player_gold",
    "player_kills", "player_is_reloading", "player_reload_end_time",
    "zombies", "items", "wave_count", "zombies_to_spawn_this_wave",
    "game_message", "game_running", "last_game_update_time"
]

# 게임 설정값
PLAYER_BASE_ATK = 20
ZOMBIE_INITIAL_HP = 50
ZOMBIE_INITIAL_ATK = 10
ZOMBIE_INITIAL_GOLD = 10
ZOMBIE_SPEED_PER_TURN = 1 # 한 턴에 좀비가 플레이어에게 가까워지는 정도 (가상 거리)
ZOMBIE_SPAWN_INTERVAL_TURNS = 2 # 좀비가 스폰되는 턴 간격
ITEMS_SPAWN_CHANCE = 0.3 # 턴 진행 시 아이템 스폰 확률
ITEM_HEAL_AMOUNT = 30
ITEM_AMMO_AMOUNT = 20
MAX_WAVES = 10 # 최종 웨이브 수 (이후 게임 클리어 목표)

# =========================
# 게임 초기화 함수
# =========================
def init_game_state():
    """
    게임의 모든 세션 상태를 초기화합니다.
    """
    st.session_state.player_hp = 100
    st.session_state.player_max_hp = 100
    st.session_state.player_current_mag_ammo = 10
    st.session_state.player_magazine_size = 10
    st.session_state.player_total_ammo = 30
    st.session_state.player_gold = 0
    st.session_state.player_kills = 0
    st.session_state.player_is_reloading = False
    st.session_state.player_reload_end_time = 0

    st.session_state.zombies = [] # [{hp: int, atk: int, gold: int, distance: float, name: str, id: int}]
    st.session_state.items = [] # [{type: str, distance: float, id: int}]

    st.session_state.wave_count = 0
    st.session_state.zombies_to_spawn_this_wave = 3 # 첫 웨이브 좀비 수
    
    st.session_state.game_message = "새로운 게임을 시작합니다!"
    st.session_state.game_running = True
    st.session_state.last_game_update_time = time.time() # 턴 간 시간 계산용

# 세션 상태가 초기화되지 않았거나 타입이 올바르지 않으면 초기화 함수 호출
for key in STATE_KEYS:
    if key not in st.session_state:
        init_game_state()
        break
# 추가적인 타입 안정성 보장
if not isinstance(st.session_state.zombies, list):
    st.session_state.zombies = []
if not isinstance(st.session_state.items, list):
    st.session_state.items = []


# =========================
# 메시지 및 UI 업데이트 유틸리티
# =========================
def show_message(msg):
    """게임 메시지를 업데이트합니다."""
    st.session_state.game_message = msg

def update_ui():
    """게임 UI의 주요 정보를 업데이트하여 표시합니다."""
    st.subheader("플레이어 상태")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("HP", f"{st.session_state.player_hp}/{st.session_state.player_max_hp}")
    col2.metric("탄약", f"{st.session_state.player_current_mag_ammo}/{st.session_state.player_total_ammo}")
    col3.metric("골드", st.session_state.player_gold)
    col4.metric("킬 수", st.session_state.player_kills)

    # HP 프로그레스 바는 항상 0과 1 사이의 값을 가지도록 보장
    progress_hp_value = max(0.0, min(1.0, st.session_state.player_hp / st.session_state.player_max_hp))
    st.progress(progress_hp_value, text="HP")

    st.subheader(f"현재 웨이브: {st.session_state.wave_count} / {MAX_WAVES}")
    st.write(f"남은 좀비: {len(st.session_state.zombies)}")

    st.info(st.session_state.game_message)

# =========================
# 게임 액션 함수
# =========================
def shoot_action():
    """
    총을 발사하는 액션을 처리합니다.
    가장 가까운 좀비를 자동으로 조준합니다.
    """
    if not st.session_state.game_running:
        return

    player_atk = PLAYER_BASE_ATK # 현재는 고정 공격력

    if st.session_state.player_is_reloading:
        show_message("재장전 중입니다...")
        return
    
    if st.session_state.player_current_mag_ammo <= 0:
        show_message("탄약이 없습니다. 재장전하세요 (R 키 또는 버튼)!")
        return

    # 가장 가까운 좀비 찾기
    if st.session_state.zombies:
        closest_zombie_index = 0
        min_distance = float('inf') # 무한대로 초기화
        for i, zombie in enumerate(st.session_state.zombies):
            if zombie['distance'] < min_distance:
                min_distance = zombie['distance']
                closest_zombie_index = i
        
        target_zombie = st.session_state.zombies[closest_zombie_index]

        # 총알 소모
        st.session_state.player_current_mag_ammo -= 1
        
        # 좀비에게 피해 입히기
        damage_dealt = player_atk + random.randint(-5, 5) # 무작위성 추가
        target_zombie['hp'] -= damage_dealt
        show_message(f"🔫 좀비에게 {damage_dealt} 피해를 입혔습니다! ({target_zombie['name']} HP: {max(0, target_zombie['hp'])})")

        # 좀비 사망 처리
        if target_zombie['hp'] <= 0:
            st.session_state.player_gold += target_zombie['gold']
            st.session_state.player_kills += 1
            st.session_state.zombies.pop(closest_zombie_index) # 좀비 제거
            show_message(f"💀 좀비 처치! 골드 +{target_zombie['gold']}, 킬 수 +1")
        
    else:
        show_message("사격할 좀비가 없습니다.")
    
    # 턴 진행 없이 바로 UI 업데이트
    st.rerun()

def reload_action():
    """
    총을 재장전하는 액션을 처리합니다.
    """
    if not st.session_state.game_running:
        return

    if st.session_state.player_is_reloading:
        show_message("이미 재장전 중입니다...")
        return
    
    if st.session_state.player_current_mag_ammo == st.session_state.player_magazine_size:
        show_message("탄창이 이미 가득 찼습니다.")
        return
    
    if st.session_state.player_total_ammo <= 0:
        show_message("재장전할 탄약이 없습니다.")
        return

    st.session_state.player_is_reloading = True
    st.session_state.player_reload_end_time = time.time() + 1.5 # 1.5초 재장전 시간
    show_message("🔄 재장전 중...")
    
    # 실제 탄약 장전은 턴 진행 시 또는 다음 UI 업데이트 시 처리
    st.rerun()

def collect_item_action(item_id):
    """아이템을 획득하는 액션을 처리합니다."""
    if not st.session_state.game_running:
        return

    item_found = None
    # items 리스트가 유효한지 다시 확인
    if isinstance(st.session_state.items, list):
        for i, item in enumerate(st.session_state.items):
            if item['id'] == item_id:
                item_found = item
                st.session_state.items.pop(i) # 아이템 제거
                break
    else:
        # 만약 items가 리스트가 아니면 초기화하고 오류 메시지 출력
        st.session_state.items = []
        show_message("게임 오류: 아이템 목록이 손상되었습니다. 리셋됩니다.")
        
    if item_found:
        if item_found['type'] == 'health':
            heal_amount = ITEM_HEAL_AMOUNT
            st.session_state.player_hp = min(st.session_state.player_max_hp, st.session_state.player_hp + heal_amount)
            show_message(f"❤️ 힐팩 획득! HP +{heal_amount}")
        elif item_found['type'] == 'ammo':
            ammo_amount = ITEM_AMMO_AMOUNT
            st.session_state.player_total_ammo += ammo_amount
            show_message(f"➕ 탄약 박스 획득! 탄약 +{ammo_amount}")
    else:
        show_message("선택한 아이템을 찾을 수 없습니다.")
    
    st.rerun()

def next_turn_action():
    """
    다음 턴으로 게임을 진행하는 액션을 처리합니다.
    좀비 생성, 이동, 공격, 재장전 완료 등을 처리합니다.
    """
    if not st.session_state.game_running:
        return

    show_message("➡️ 다음 턴으로 진행합니다...")

    # 재장전 완료 처리
    if st.session_state.player_is_reloading:
        if time.time() >= st.session_state.player_reload_end_time:
            ammo_to_reload = min(
                st.session_state.player_magazine_size - st.session_state.player_current_mag_ammo,
                st.session_state.player_total_ammo
            )
            st.session_state.player_current_mag_ammo += ammo_to_reload
            st.session_state.player_total_ammo -= ammo_to_reload
            st.session_state.player_is_reloading = False
            show_message("재장전 완료!")
        else:
            show_message("재장전 중...")
            # 재장전 중에는 턴 진행이 안 되는 대신 다른 액션도 불가 (현재는 UI 버튼 활성화/비활성화로 제어)

    # 좀비 생성
    if st.session_state.wave_count < MAX_WAVES:
        if len(st.session_state.zombies) == 0: # 현재 웨이브 좀비가 없으면 다음 웨이브 시작
            st.session_state.wave_count += 1
            st.session_state.zombies_to_spawn_this_wave = st.session_state.wave_count * 2 + 1 # 웨이브별 좀비 수 증가
            show_message(f"새로운 웨이브 {st.session_state.wave_count} 시작! 좀비 {st.session_state.zombies_to_spawn_this_wave}마리 출현!")
            
            for _ in range(st.session_state.zombies_to_spawn_this_wave):
                spawn_zombie()
        elif random.random() < 0.5 and len(st.session_state.zombies) < st.session_state.zombies_to_spawn_this_wave:
            # 웨이브 도중에도 일정 확률로 좀비 추가 스폰
            spawn_zombie()

    # 좀비 이동 및 공격
    # zombies 리스트가 유효한지 다시 확인
    if isinstance(st.session_state.zombies, list):
        for zombie in st.session_state.zombies:
            zombie['distance'] = max(0, zombie['distance'] - ZOMBIE_SPEED_PER_TURN) # 플레이어에게 가까워짐

            if zombie['distance'] <= 0:
                damage_taken = zombie['atk']
                st.session_state.player_hp -= damage_taken
                show_message(f"💢 좀비에게 {damage_taken} 피해를 입었습니다! (HP: {st.session_state.player_hp})")
                zombie['distance'] = 1 # 더 이상 다가오지 못하게 잠시 멈춤
    else:
        # zombies가 리스트가 아니면 초기화하고 오류 메시지 출력
        st.session_state.zombies = []
        show_message("게임 오류: 좀비 목록이 손상되었습니다. 리셋됩니다.")


    # 아이템 스폰
    # items 리스트가 유효한지 다시 확인
    if isinstance(st.session_state.items, list):
        if random.random() < ITEMS_SPAWN_CHANCE and len(st.session_state.items) < 3: # 최대 3개까지 스폰
            spawn_item()
    else:
        # items가 리스트가 아니면 초기화하고 오류 메시지 출력
        st.session_state.items = []
        show_message("게임 오류: 아이템 목록이 손상되었습니다. 리셋됩니다.")


    # 게임 종료/승리 조건 체크
    if st.session_state.player_hp <= 0:
        st.session_state.player_hp = 0 # 음수 방지
        st.session_state.game_running = False
        show_message("☠️ 플레이어가 쓰러졌습니다... 게임 오버!")
    elif st.session_state.wave_count >= MAX_WAVES and len(st.session_state.zombies) == 0:
        st.session_state.game_running = False
        show_message("🎉🎉 게임 클리어! 모든 좀비를 물리쳤습니다!")

    st.rerun()

# =========================
# 좀비 및 아이템 생성 (내부 함수)
# =========================
_zombie_id_counter = 0
def spawn_zombie():
    """새로운 좀비를 생성하여 좀비 리스트에 추가합니다."""
    global _zombie_id_counter
    # 웨이브 진행에 따라 좀비 능력치 강화
    hp_boost = st.session_state.wave_count * 10
    atk_boost = st.session_state.wave_count * 2
    
    new_zombie = {
        'id': _zombie_id_counter,
        'name': random.choice(["일반 좀비", "빠른 좀비", "강한 좀비"]),
        'hp': ZOMBIE_INITIAL_HP + hp_boost + random.randint(0, 20),
        'atk': ZOMBIE_INITIAL_ATK + atk_boost + random.randint(0, 5),
        'gold': ZOMBIE_INITIAL_GOLD + random.randint(0, 5),
        'distance': random.randint(5, 15) # 플레이어로부터의 가상 거리
    }
    _zombie_id_counter += 1
    st.session_state.zombies.append(new_zombie)
    # show_message(f"{new_zombie['name']}가 나타났다! (거리: {new_zombie['distance']})")

_item_id_counter = 0
def spawn_item():
    """새로운 아이템을 생성하여 아이템 리스트에 추가합니다."""
    global _item_id_counter
    item_type = random.choice(['health', 'ammo'])
    new_item = {
        'id': _item_id_counter,
        'type': item_type,
        'distance': random.randint(3, 10) # 플레이어로부터의 가상 거리
    }
    _item_id_counter += 1
    st.session_state.items.append(new_item)
    show_message(f"✨ {item_type} 아이템이 나타났다! (거리: {new_item['distance']})")

# =========================
# 메인 Streamlit 앱 레이아웃
# =========================
st.set_page_config(page_title="Streamlit 좀비 슈터", page_icon="🧟", layout="centered")

st.title("🧟‍♂️ Streamlit 좀비 슈터 RPG")
st.write("턴 기반의 간단한 좀비 슈터 게임입니다. 버튼을 클릭하여 좀비로부터 살아남으세요!")

# 게임 UI 표시
update_ui()

# 게임 상태에 따른 버튼 및 메시지
if st.session_state.game_running:
    st.markdown("---")
    st.subheader("액션")
    col_actions = st.columns(3)

    with col_actions[0]:
        if st.button("🔫 공격", key="shoot_button", disabled=st.session_state.player_is_reloading or len(st.session_state.zombies) == 0):
            shoot_action()
    
    with col_actions[1]:
        if st.button("🔄 재장전", key="reload_button", disabled=st.session_state.player_is_reloading or st.session_state.player_current_mag_ammo == st.session_state.player_magazine_size or st.session_state.player_total_ammo == 0):
            reload_action()
    
    with col_actions[2]:
        if st.button("➡️ 턴 진행", key="next_turn_button", disabled=st.session_state.player_is_reloading and (time.time() < st.session_state.player_reload_end_time)):
            next_turn_action()

    st.markdown("---")
    st.subheader("맵 상태")

    # 플레이어 위치 표시
    player_col_idx = 4 # 9개 열 중 중앙 (0-8)
    cols = st.columns(9)
    with cols[player_col_idx]:
        st.write("🧍") # 플레이어

    # 좀비 표시
    if st.session_state.zombies:
        st.write("--- 좀비 ---")
        for zombie in st.session_state.zombies:
            zombie_icon = "🧟" if "일반" in zombie['name'] else ("🏃" if "빠른" in zombie['name'] else "💪")
            st.write(f"{zombie_icon} {zombie['name']} (HP: {max(0, zombie['hp'])}) - 거리: {zombie['distance']:.1f}")
    else:
        st.write("좀비 없음! 다음 턴을 진행하세요.")

    # 아이템 표시
    if st.session_state.items:
        st.write("--- 아이템 ---")
        for item in st.session_state.items:
            item_icon = "❤️" if item['type'] == 'health' else "➕"
            if st.button(f"{item_icon} {item['type']} 획득 (거리: {item['distance']:.1f})", key=f"item_collect_{item['id']}"):
                collect_item_action(item['id'])
    else:
        st.write("맵에 아이템이 없습니다.")

else: # 게임 종료 (오버 또는 클리어)
    st.markdown("---")
    if st.session_state.player_hp <= 0:
        st.error("게임 오버! 좀비에게 당했습니다...")
    elif st.session_state.wave_count >= MAX_WAVES and len(st.session_state.zombies) == 0:
        st.success("🎉 게임 클리어! 모든 웨이브를 막아냈습니다!")
        st.balloons()
    
    if st.button("새 게임 시작", key="restart_game_final"):
        init_game_state()
        st.rerun()
