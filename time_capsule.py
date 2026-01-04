import streamlit as st
import datetime
import json
import os

# --- 설정 ---
DATA_FILE = "capsule_data.json"
TARGET_HOUR = 19  # 저녁 7시 (19:00)

# --- 헬퍼 함수: 다음 주 토요일 저녁 7시 계산 ---
def get_open_time():
    now = datetime.datetime.now()
    # weekday(): 월=0, ... 토=5, 일=6
    # 오늘이 토요일(5)이면 7일 뒤, 아니면 다가오는 토요일 계산
    days_ahead = 5 - now.weekday()
    
    if days_ahead <= 0: # 이미 토요일이 지났거나 오늘인 경우 다음주로 넘길지 결정
        # 여기서는 단순하게 "오늘이 토요일이어도 다음주 토요일"로 설정 (7일 + 남은일수)
        # 만약 "이번주 토요일"을 원하면 로직 조정 가능
        days_ahead += 7
        
    next_saturday = now + datetime.timedelta(days=days_ahead)
    target_time = next_saturday.replace(hour=TARGET_HOUR, minute=0, second=0, microsecond=0)
    return target_time

# --- 데이터 저장/로드 함수 ---
def load_messages():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_message(name, message):
    messages = load_messages()
    messages.append({
        "name": name,
        "message": message,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

# --- 메인 앱 로직 ---
def main():
    st.set_page_config(page_title="우리만의 타임캡슐", page_icon="🕰️")
    
    st.title("🕰️ 5인의 타임캡슐")
    st.markdown("---")

    # 1. 시간 확인
    target_time = get_open_time()
    now = datetime.datetime.now()
    
    # 시간 디버깅용 (테스트할 때만 주석 해제하세요)
    # st.write(f"현재 시간: {now}")
    # st.write(f"개봉 예정: {target_time}")

    messages = load_messages()
    current_count = len(messages)
    
    # 2. 개봉 시간 전/후 로직
    if now < target_time:
        # === 잠김 상태 (LOCK) ===
        st.info(f"🔒 타임캡슐이 봉인되어 있습니다.\n\n개봉 일시: {target_time.strftime('%Y년 %m월 %d일 %H시 %M분')}")
        
        # 현황판
        st.subheader(f"현재 참여 현황 ({current_count}/5)")
        for msg in messages:
            st.text(f"👤 {msg['name']}님이 메시지를 넣었습니다. (내용 비공개)")
            
        st.markdown("---")
        
        # 입력 폼 (5명이 다 차면 입력 막기)
        if current_count < 5:
            st.write("### 📝 타임캡슐에 메시지 남기기")
            with st.form("capsule_form"):
                name = st.text_input("닉네임")
                msg_input = st.text_area("미래의 우리에게 남길 말 (비공개)")
                submitted = st.form_submit_button("캡슐에 넣기")
                
                if submitted:
                    if name and msg_input:
                        save_message(name, msg_input)
                        st.success("메시지가 안전하게 봉인되었습니다! 개봉일에 만나요.")
                        st.rerun()
                    else:
                        st.warning("닉네임과 내용을 모두 입력해주세요.")
        else:
            st.success("🎉 5명의 메시지가 모두 모였습니다! 개봉 시간만 기다리세요.")
            
    else:
        # === 열림 상태 (OPEN) ===
        st.balloons()
        st.success(f"🔓 타임캡슐이 개봉되었습니다! ({target_time.strftime('%Y-%m-%d')} 기준)")
        st.markdown("### 💌 도착한 메시지들")
        
        for idx, msg in enumerate(messages):
            with st.container():
                st.markdown(f"**To. 모두에게 (By. {msg['name']})**")
                st.info(msg['message'])
                st.caption(f"작성일: {msg['timestamp']}")
                st.markdown("---")

if __name__ == "__main__":
    main()
