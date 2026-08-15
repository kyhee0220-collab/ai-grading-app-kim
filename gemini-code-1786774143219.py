import streamlit as st
import re

# ==========================================
# 1. 자동 채점 로직 (Rule Engine)
# ==========================================

def validate_element_a_content(elem_a, required_patterns):
    """
    [요소 A] 내에 [필요한 내용]이 필수적으로 포함되어 있는지 검증하는 함수
    elem_a: 학생이 작성한 [요소 A] 문장
    required_patterns: [필요한 내용]을 상징하는 정규표현식 패턴 목록
    """
    for pattern in required_patterns:
        if re.search(pattern, elem_a):
            return True, "필수 내용 포함 확인"
    return False, "[요소 A]에 조건에서 요구하는 [필요한 내용]이 누락됨"


def check_logical_connection(elem_a, elem_b, semantic_map):
    """[요소 A]와 [요소 B] 간의 실질적 의미 연결성을 검증하는 함수"""
    for a_keywords, b_keywords in semantic_map:
        if any(re.search(a_kw, elem_a) for a_kw in a_keywords):
            if any(re.search(b_kw, elem_b) for b_kw in b_keywords):
                return True, "연결성 통과"
            else:
                return False, f"요소 A('{elem_a}')와 요소 B('{elem_b}')가 내용상 연결되지 않음"
    return True, "기본 통과"


def grade_set1_q3(visual_plan, visual_effect, audio_plan, audio_effect):
    """실전 적용-1 [서·논술형 3] 채점 (요소 A 필수 내용 검증 강화)"""
    score = 0
    feedback = []

    # ----------------------------------------------------
    # 1. 시각 영역: [요소 A = 시각 연출] / [요소 B = 시각 효과]
    # ----------------------------------------------------
    # [요소 A]에 반드시 들어가야 할 [필요한 내용] 패턴 (혼자/독립/책상/단독 등)
    vis_required_a = [r"혼자", r"독립", r"책상", r"방", r"차분", r"단독"]
    is_vis_a_valid, vis_a_msg = validate_element_a_content(visual_plan, vis_required_a)

    if is_vis_a_valid:
        score += 1
        feedback.append("시각 연출 정답 (1점): [요소 A]에 필요한 핵심 연출 내용이 적절히 포함됨")
    else:
        feedback.append(f"시각 연출 오답 (0점 - 필수 내용 누락): 작성된 [요소 A]('{visual_plan}')에 조건에서 요구하는 [필요한 내용](예: 혼자/독립된 공간/책상 등)이 담겨 있지 않음")

    # [요소 B] 효과 및 A-B 연결성 검증
    vis_effect_kw = r"(어려운\s*과제|도전|집중|방해|사회적\s*억제)"
    has_vis_conclusion = bool(re.search(r"(효과가\s*있다|강조한다|보여준다|전달한다|돋보이게\s*한다)", visual_effect))
    vis_semantic_map = [([r"혼자", r"방", r"책상"], [r"어려운\s*과제", r"집중", r"사회적\s*억제"])]
    is_vis_connected, _ = check_logical_connection(visual_plan, visual_effect, vis_semantic_map)

    if is_vis_a_valid:
        if re.search(vis_effect_kw, visual_effect) and has_vis_conclusion:
            if is_vis_connected:
                score += 2
                feedback.append("시각 효과 정답 (2점): 시각 연출(요소 A)과 효과 서술(요소 B)이 논리적으로 긴밀히 연결됨")
            else:
                feedback.append(f"시각 효과 오답 (0점 - 논리적 연결 오류): [요소 A]('{visual_plan}')와 [요소 B]('{visual_effect}')의 내용이 서로 호응하지 않음")
        elif re.search(vis_effect_kw, visual_effect) and not has_vis_conclusion:
            feedback.append("시각 효과 오답 (0점 - 결론 누락): 근거는 있으나 최종 효과/결론 서술이 불명확함")
        else:
            feedback.append("시각 효과 오답 (0점): 지문 내용 근거 누락")
    else:
        feedback.append("시각 효과 오답 (0점): [요소 A]의 내용이 올바르지 않아 연계된 효과도 인정 불가")


    # ----------------------------------------------------
    # 2. 청각 영역: [요소 A = 청각 연출] / [요소 B = 청각 효과]
    # ----------------------------------------------------
    # [요소 A]에 반드시 들어가야 할 [필요한 내용] 패턴 (정적/고요/초침/소리 없음 등)
    aud_required_a = [r"정적", r"고요", r"초침", r"배경음\s*없", r"소리\s*없"]
    is_aud_a_valid, aud_a_msg = validate_element_a_content(audio_plan, aud_required_a)

    if is_aud_a_valid:
        score += 1
        feedback.append("청각 연출 정답 (1점): [요소 A]에 필요한 핵심 연출 내용이 적절히 포함됨")
    else:
        feedback.append(f"청각 연출 오답 (0점 - 필수 내용 누락): 작성된 [요소 A]('{audio_plan}')에 조건에서 요구하는 [필요한 내용](예: 정적/고요함/배경음 없음 등)이 담겨 있지 않음")

    # [요소 B] 효과 및 A-B 연결성 검증
    aud_effect_kw = r"(소음|방해|혼자|집중|사회적\s*억제)"
    has_aud_conclusion = bool(re.search(r"(효과가\s*있다|강조한다|보여준다|전달한다|극대화한다)", audio_effect))
    aud_semantic_map = [([r"정적", r"고요", r"초침", r"배경음\s*없"], [r"소음", r"방해", r"집중", r"사회적\s*억제"])]
    is_aud_connected, _ = check_logical_connection(audio_plan, audio_effect, aud_semantic_map)

    if is_aud_a_valid:
        if re.search(aud_effect_kw, audio_effect) and has_aud_conclusion:
            if is_aud_connected:
                score += 2
                feedback.append("청각 효과 정답 (2점): 청각 연출(요소 A)과 효과 서술(요소 B)이 논리적으로 긴밀히 연결됨")
            else:
                feedback.append(f"청각 효과 오답 (0점 - 논리적 연결 오류): [요소 A]('{audio_plan}')와 [요소 B]('{audio_effect}')의 내용이 서로 상응하지 않음")
        elif re.search(aud_effect_kw, audio_effect) and not has_aud_conclusion:
            feedback.append("청각 효과 오답 (0점 - 결론 누락): 근거는 있으나 최종 효과/결론 서술이 불명확함")
        else:
            feedback.append("청각 효과 오답 (0점): 지문 속 개념과의 연계성 미흡")
    else:
        feedback.append("청각 효과 오답 (0점): [요소 A]의 내용이 올바르지 않아 연계된 효과도 인정 불가")

    return score, feedback


# ==========================================
# 2. Streamlit UI 화면 구성
# ==========================================

st.set_page_config(page_title="서·논술형 자동 채점 시스템", layout="wide")

st.title("📝 국어 서·논술형 문항 자동 채점 시스템")
st.caption("[요소 A] 필수 내용 포함 여부 검증 알고리즘 적용")

st.sidebar.header("📌 세트 선택")
selected_set = st.sidebar.selectbox("채점할 문항 세트를 선택하세요", ["실전 적용-1 (사회적 촉진/억제)"])

if selected_set == "실전 적용-1 (사회적 촉진/억제)":
    st.header(" [실전 적용-1] 서·논술형 3번 ([요소 A] 필수 내용 누락 검증 시연)")
    st.caption("💡 **테스트 가이드**: [요소 A](시각 연출)에 '예쁜 카페에서 활기차게 웃는 장면'처럼 필요한 내용('혼자/독립된 공간')이 누락되면 **[요소 A] 및 연계된 [요소 B]까지 모두 오답 처리**됩니다.")

    v_plan = st.text_input("Ⓐ 시각 연출 계획 [요소 A]:", value="화려하고 넓은 도서관에서 여러 명이 어울리는 모습") # 필수 내용 누락 테스트용
    v_eff = st.text_area("Ⓐ 시각 연출 효과 [요소 B]:", value="어려운 과제를 할 때 집중력을 높여주는 효과가 있다.")
    
    a_plan = st.text_input("Ⓑ 청각 연출 계획 [요소 A]:", value="배경음악 없이 시계 초침 소리만 잔잔하게 들리도록 한다.") # 정상 입력
    a_eff = st.text_area("Ⓑ 청각 연출 효과 [요소 B]:", value="주변 소음을 제거하여 방해받지 않고 혼자 집중해야 하는 '사회적 억제' 상황의 특성을 청각적으로 전달하는 효과가 있다.")
    
    if st.button("채점 실행하기"):
        score, feedback = grade_set1_q3(v_plan, v_eff, a_plan, a_eff)
        st.metric("최종 점수", f"{score} / 6 점")
        st.subheader("채점 피드백 상세")
        for fb in feedback:
            if "오답" in fb:
                st.error("- " + fb)
            else:
                st.success("- " + fb)